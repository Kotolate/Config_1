import argparse
import os
import tarfile
from datetime import datetime
import xml.etree.ElementTree as ET

class ShellEmulator:
    def __init__(self, username, tar, log):
        self.username = username
        self.tar_path = tar
        self.log_path = log
        self.current_dir = 'tests/'
        self.file_system = self.load_tar()


    def load_tar(self):
        if not os.path.exists(self.tar_path):
            print(f"File not found: {self.tar_path}")
            return []
        with tarfile.open(self.tar_path, 'r') as tar:
            return [f for f in tar.getnames()]

    def load_log(self):
        if os.path.exists(self.log_path):
            print(f"Loading log from: {self.log_path}")
            tree = ET.parse(self.log_path)
            root = tree.getroot()
            for action in root.findall("action"):
                user = action.find("user").text
                timestamp = action.find("timestamp").text
                command = action.find("command").text
                print(f"Loading log from: {self.log_path}")


    def prompt(self):
        print(f"{self.username}@emulator:{self.current_dir}~$ ", end="")

    def log_action(self, command):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not os.path.exists(self.log_path):
            tree = ET.ElementTree(ET.Element("log"))
        else:
            tree = ET.parse(self.log_path)
        root = tree.getroot()
        action = ET.SubElement(root, "action")
        user = ET.SubElement(action, "user")
        user.text = self.username
        timestamp_elem = ET.SubElement(action, "timestamp")
        timestamp_elem.text = timestamp
        cmd = ET.SubElement(action, "command")
        cmd.text = command
        tree.write(self.log_path)

    def execute_command(self, command):

        self.log_action(command)

        cmd_parts = command.split()
        if cmd_parts:
            cmd = cmd_parts[0]
            if cmd == 'exit':
                return False
            elif cmd == 'ls':
                self.list_files()
            elif cmd == 'cd':
                self.change_directory(cmd_parts[1] if len(cmd_parts) > 1 else '')
            elif cmd == 'rmdir':
                self.rmdir(cmd_parts[1] if len(cmd_parts) > 1 else '')
            elif cmd == 'tree':
                self.tree()
            elif cmd == 'tac':
                if len(cmd_parts) > 1:
                    self.tac(cmd_parts[1])
                else:
                    print("tac requires a filename argument")
            else:
                print(f"Unknown command: {cmd}")
        self.prompt()
        return True

    def list_files(self):
        current_files = [f for f in self.file_system if f.startswith(self.current_dir)]
        if current_files:
            all=""
            for file in current_files:
                print(file[len(self.current_dir):])
                all+=file[len(self.current_dir):]
            return all
        else:
            print("No files found")

    def change_directory(self, directory):
        if directory == '..':
            self.current_dir = '/'.join(self.current_dir.split('/')[:-2]) + '/' if self.current_dir != '' else ''
        else:
            full_path = self.current_dir + directory
            if full_path in self.file_system:
                self.current_dir = full_path + '/'
            else:
                print(f"No such directory: {directory}")

    def rmdir(self, dirname):
        full_path = self.current_dir+dirname
        if full_path in self.file_system and os.path.isdir(full_path):
            subdirs = [f for f in self.file_system if f.startswith(full_path + "/")]
            if subdirs:
                print(f"Directory '{dirname}' is not empty.")
                return
            self.file_system.remove(full_path)
            print(f"Removed directory: {dirname}")
        else:
            print(f"Directory not found or not a directory: {dirname}")

    def tree(self):
        output=[]
        self.print_tree(self.file_system, self.current_dir,output)
        print("\n".join(output))
        return output


    def print_tree(self, file_system, current_path, output, indent=0):
        files = sorted([f for f in file_system if f.startswith(current_path)])

        for file in files:
            relative_path = os.path.relpath(file, current_path)
            parts = relative_path.split(os.sep)
            level = len(parts) -1

            if level >=0 :
                output.append('  ' * level + parts[-1])

            if os.path.isdir(file) and len(file) > len(current_path):
                self.print_tree(file_system, file + os.sep, output, indent)



    def tac(self, filename):
        full_path = os.path.join(self.current_dir, filename)
        if full_path in self.file_system:
            with tarfile.open(self.tar_path, 'r') as tar:

                file_member = tar.getmember(full_path)
                if file_member.isfile():
                    with tar.extractfile(file_member) as f:
                        content = f.read().decode('utf-8').splitlines()
                        out="\n".join(reversed(content))
                        print(out)
                        return out
                else:
                    print(f"{filename} is not a file")
                    return False
        else:
            print(f"No such file: {filename}")
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("--username", required=False, default="Config_1", help="Username")
    parser.add_argument("--tar", required=False, default="tests.tar", help="Путь к архиву tar")
    parser.add_argument("--log", required=False, default="emulatorlog.xml", help="Путь к лог файлу")
    args = parser.parse_args()

    emulator = ShellEmulator(args.username, args.tar, args.log)
    emulator.prompt()
    while True:
        command = input()
        if not emulator.execute_command(command):
            break