import unittest
import os
import tarfile
import tempfile
from main import ShellEmulator


class TestEmulator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tar_path = os.path.join(self.temp_dir.name, "tests.tar")
        self.log_path = os.path.join(self.temp_dir.name, "log.xml")

        # Create a more complex test filesystem
        os.makedirs(os.path.join(self.temp_dir.name, "tests/dir1/subdir1"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir.name, "tests/dir2"), exist_ok=True)
        with open(os.path.join(self.temp_dir.name, "tests/file1.txt"), "w") as f:
            f.write("one\ntwo")
        with open(os.path.join(self.temp_dir.name, "tests/dir1/file2.txt"), "w") as f:
            f.write("two\nthree")
        with open(os.path.join(self.temp_dir.name, "tests/dir1/subdir1/file3.txt"), "w") as f:
            f.write("")


        with tarfile.open(self.tar_path, "w") as tar:
            tar.add(os.path.join(self.temp_dir.name, "tests"), arcname="tests")

        with open(self.log_path, "w", encoding="utf-8") as log_file:
            log_file.write("<log></log>")

        self.emulator = ShellEmulator(None, self.tar_path, self.log_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_exit_1(self):
        self.assertFalse(self.emulator.execute_command("exit"))

    def test_exit_2(self):
        self.emulator.change_directory("dir1/subdir1")
        self.assertFalse(self.emulator.execute_command("exit"))

    def test_exit_3(self):
        self.emulator.change_directory("dir1")
        self.assertFalse(self.emulator.execute_command("exit"))

    def test_ls_1(self):
        self.assertIn("file1.txt", self.emulator.list_files())

    def test_ls_2(self):
        self.emulator.change_directory("dir1")
        self.assertIn("file2.txt", self.emulator.list_files())

    def test_ls_3(self):
        self.emulator.change_directory("dir1")
        self.assertIn("subdir1", self.emulator.list_files())


    def test_cd_1(self):
        self.emulator.change_directory("dir1")
        self.assertEqual(self.emulator.current_dir, "tests/dir1/")

    def test_cd_2(self):
        self.emulator.change_directory("dir1/subdir1")
        self.assertEqual(self.emulator.current_dir, "tests/dir1/subdir1/")

    def test_cd_3(self):
        self.emulator.change_directory("dir1/subdir1")
        self.emulator.change_directory("..")
        self.assertEqual(self.emulator.current_dir, "tests/dir1/")

    def test_rmdir_1(self):
        self.emulator.rmdir("dir2")
        self.assertNotIn("tests/dir2", self.emulator.file_system)

    def test_rmdir_2(self):
        self.emulator.rmdir("dir1")
        self.assertIn("tests/dir1", self.emulator.file_system)

    def test_rmdir_3(self):
        self.emulator.change_directory("dir1/subdir1")
        self.emulator.rmdir("dir2")
        self.assertIn("tests/dir2", self.emulator.file_system)

    def test_tree_1(self):
        tree_output = self.emulator.tree()
        self.assertIn("dir1", tree_output)
        self.assertIn("dir2", tree_output)
        self.assertIn("  subdir1", tree_output)

    def test_tree_2(self):
        self.emulator.change_directory("dir1")
        tree_output = self.emulator.tree()
        self.assertIn("file2.txt", tree_output)
        self.assertNotIn("dir2", tree_output)

    def test_tree_3(self):
        self.emulator.change_directory("dir1/subdir1")
        tree_output = self.emulator.tree()
        self.assertEqual(["file3.txt"],tree_output)

    def test_tac_1(self):
        self.emulator.change_directory("dir1")
        tac=self.emulator.tac("file2.txt")
        self.assertIn("three\ntwo", tac)

    def test_tac_2(self):
        tac=self.emulator.tac("file1.txt")
        self.assertIn("two\none", tac)

    def test_tac_3(self):
        tac=self.emulator.tac("file31.txt")
        self.assertEqual(False, tac)

    if __name__ == '__main__':
        unittest.main()