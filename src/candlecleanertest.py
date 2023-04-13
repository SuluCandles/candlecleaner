import unittest
import os
import shutil
from unittest.mock import patch
from candlecleaner import CleanerApp

class TestCleanerApp(unittest.TestCase):
    def setUp(self):
        self.app = CleanerApp(True)
        self.directory = os.getcwd()

    def test_select_directory(self):
        with patch('tkinter.filedialog.askdirectory', return_value=self.directory):
            self.app.select_directory()
            self.assertEqual(self.app.directory_var.get(), self.directory)

    def test_validate_string_entry(self):
        self.app.smart_update_var.set(True)
        self.app.validate_string_entry()
        self.assertEqual(self.app.string_entry.cget('state'), 'disabled')

        self.app.smart_update_var.set(False)
        self.app.validate_string_entry()
        self.assertEqual(self.app.string_entry.cget('state'), 'normal')

    def test_update_file_list(self):
        self.app.directory_var.set(self.directory)
        self.app.update_file_list()
        self.assertNotEqual(len(self.app.file_tree.get_children()), 0)
        self.assertNotEqual(len(self.app.updated_file_tree.get_children()), 0)

    # .
    # ├── .DS_Store
    # ├── .btest_file7.txt
    # ├── .test_file1.txt
    # ├── .test_file2.txt
    # ├── btest_file7.txt
    # ├── test_file1.txt
    # ├── test_file2.txt
    # ├── subdir1
    # │   ├── .DS_Store
    # │   ├── .test_file3.txt
    # │   ├── .test_file4.txt
    # │   ├── test_file3.txt
    # │   └── test_file4.txt
    # ├── subdir2
    # │   ├── .DS_Store
    # │   ├── .test_file5.txt
    # │   ├── .test_file6.txt
    # │   ├── test_file5.txt
    # │   └── test_file6.txt
    # └── subdir3
    #     └── .DS_Store
    def test_rename_files(self):
        # Test renaming files in a temporary directory
        temp_directory = 'tmp'
        os.mkdir(temp_directory)
        os.chdir(temp_directory)

        open('test_file1.txt', 'w').close()
        open('test_file2.txt', 'w').close()
        open('btest_file7.txt', 'w').close()
        open('.test_file1.txt', 'w').close()
        open('.test_file2.txt', 'w').close()
        open('.btest_file7.txt', 'w').close()
        open('.DS_Store', 'w').close()
        # Create two subdirectories and two files within each subdirectory to be renamed
        os.mkdir('subdir1')
        open('subdir1/test_file3.txt', 'w').close()
        open('subdir1/test_file4.txt', 'w').close()
        open('subdir1/.test_file3.txt', 'w').close()
        open('subdir1/.test_file4.txt', 'w').close()
        open('subdir1/.DS_Store', 'w').close()

        os.mkdir('subdir2')
        open('subdir2/test_file5.txt', 'w').close()
        open('subdir2/test_file6.txt', 'w').close()
        open('subdir2/.test_file5.txt', 'w').close()
        open('subdir2/.test_file6.txt', 'w').close()
        open('subdir2/.DS_Store', 'w').close()

        os.mkdir('subdir3')
        open('subdir3/.DS_Store', 'w').close()

        self.app.directory_var.set(os.getcwd())
        self.app.string_var.set('test_')
        self.app.update_file_list()

        # Define the callback function for the messagebox.showinfo function
        def messagebox_callback(title, message):
            # Print the message for debugging purposes
            print(message)
            # Return the desired result (in this case, "ok")
            return "OK"

        # Use patch to replace the messagebox.showinfo function with the callback function
        with patch('tkinter.messagebox.showinfo', side_effect=messagebox_callback):
            self.app.rename_files()

        # Check that the files have been renamed correctly
        self.assertFalse(os.path.exists('test_file1.txt'))
        self.assertFalse(os.path.exists('test_file2.txt'))
        self.assertFalse(os.path.exists('btest_file7.txt'))
        self.assertFalse(os.path.exists('.test_file1.txt'))
        self.assertFalse(os.path.exists('.test_file2.txt'))
        self.assertFalse(os.path.exists('.btest_file7.txt'))
        self.assertTrue(os.path.exists('file1.txt'))
        self.assertTrue(os.path.exists('file2.txt'))
        self.assertTrue(os.path.exists('bfile7.txt'))
        self.assertTrue(os.path.exists('.file1.txt'))
        self.assertTrue(os.path.exists('.file2.txt'))
        self.assertTrue(os.path.exists('.bfile7.txt'))
        self.assertTrue(os.path.exists('.DS_Store'))

        self.assertFalse(os.path.exists('subdir1/test_file3.txt'))
        self.assertFalse(os.path.exists('subdir1/test_file4.txt'))
        self.assertFalse(os.path.exists('subdir1/.test_file3.txt'))
        self.assertFalse(os.path.exists('subdir1/.test_file4.txt'))
        self.assertTrue(os.path.exists('subdir1/file3.txt'))
        self.assertTrue(os.path.exists('subdir1/file4.txt'))
        self.assertTrue(os.path.exists('subdir1/.file3.txt'))
        self.assertTrue(os.path.exists('subdir1/.file4.txt'))
        self.assertTrue(os.path.exists('subdir1/.DS_Store'))

        self.assertFalse(os.path.exists('subdir2/test_file5.txt'))
        self.assertFalse(os.path.exists('subdir2/test_file6.txt'))
        self.assertFalse(os.path.exists('subdir2/.test_file5.txt'))
        self.assertFalse(os.path.exists('subdir2/.test_file6.txt'))  
        self.assertTrue(os.path.exists('subdir2/file5.txt'))
        self.assertTrue(os.path.exists('subdir2/file6.txt'))      
        self.assertTrue(os.path.exists('subdir2/.file5.txt'))
        self.assertTrue(os.path.exists('subdir2/.file6.txt'))
        self.assertTrue(os.path.exists('subdir2/.DS_Store'))

        self.assertTrue(os.path.exists('subdir3/.DS_Store'))

        # Clean up the temporary directory
        os.chdir('..')
        shutil.rmtree(temp_directory)

    #     .
    # ├── .DS_Store
    # ├── test_cool1.txt
    # ├── test_sad2.txt
    # ├── .test_cool1.txt
    # ├── .test_sad2.txt
    # ├── .test_really7.txt
    # ├── subdir1
    # │   ├── .DS_Store
    # │   ├── .test_mellow3.txt
    # │   ├── .test_wild4.txt
    # │   ├── test_mellow3.txt
    # │   └── test_wild4.txt
    # ├── subdir2
    # │   ├── .DS_Store
    # │   ├── .test_normal6.txt
    # │   ├── .test_weird5.txt
    # │   ├── test_normal6.txt
    # │   └── test_weird5.txt
    # └── subdir3
    #     └── .DS_Store
    def test_generate_regex(self):
        # Test renaming files in a temporary directory
        temp_directory = 'tmp'
        os.mkdir(temp_directory)
        os.chdir(temp_directory)

        open('test_cool1.txt', 'w').close()
        open('test_sad2.txt', 'w').close()
        open('.test_cool1.txt', 'w').close()
        open('.test_sad2.txt', 'w').close()
        open('.test_really7.txt', 'w').close()
        open('.DS_Store', 'w').close()
        # Create two subdirectories and two files within each subdirectory to be renamed
        os.mkdir('subdir1')
        open('subdir1/test_mellow3.txt', 'w').close()
        open('subdir1/test_wild4.txt', 'w').close()
        open('subdir1/.test_mellow3.txt', 'w').close()
        open('subdir1/.test_wild4.txt', 'w').close()
        open('subdir1/.DS_Store', 'w').close()

        os.mkdir('subdir2')
        open('subdir2/test_weird5.txt', 'w').close()
        open('subdir2/test_normal6.txt', 'w').close()
        open('subdir2/.test_weird5.txt', 'w').close()
        open('subdir2/.test_normal6.txt', 'w').close()
        open('subdir2/.DS_Store', 'w').close()

        os.mkdir('subdir3')
        open('subdir3/.DS_Store', 'w').close()

        self.app.directory_var.set(os.getcwd())
        self.app.update_file_list()
        self.app.smart_update_var.set(True)

        # Define the callback function for the messagebox.showinfo function
        def messagebox_callback(title, message):
            # Print the message for debugging purposes
            print(message)
            # Return the desired result (in this case, "ok")
            return "OK"

        # Use patch to replace the messagebox.showinfo function with the callback function
        with patch('tkinter.messagebox.showinfo', side_effect=messagebox_callback):
            self.app.rename_files()

        # Check that the files have been renamed correctly
        self.assertFalse(os.path.exists('test_cool1.txt'))
        self.assertFalse(os.path.exists('test_sad2.txt'))
        self.assertFalse(os.path.exists('.test_cool1.txt'))
        self.assertFalse(os.path.exists('.test_sad2.txt'))
        self.assertFalse(os.path.exists('.test_really7.txt'))
        self.assertFalse(os.path.exists('test_really7.txt'))
        self.assertFalse(os.path.exists('really7.txt'))
        self.assertTrue(os.path.exists('cool1.txt'))
        self.assertTrue(os.path.exists('sad2.txt'))
        self.assertTrue(os.path.exists('.cool1.txt'))
        self.assertTrue(os.path.exists('.sad2.txt'))
        self.assertTrue(os.path.exists('.really7.txt'))
        self.assertTrue(os.path.exists('.DS_Store'))

        self.assertFalse(os.path.exists('subdir1/test_mellow3.txt'))
        self.assertFalse(os.path.exists('subdir1/test_wild4.txt'))
        self.assertFalse(os.path.exists('subdir1/.test_mellow3.txt'))
        self.assertFalse(os.path.exists('subdir1/.test_wild4.txt'))
        self.assertTrue(os.path.exists('subdir1/mellow3.txt'))
        self.assertTrue(os.path.exists('subdir1/wild4.txt'))
        self.assertTrue(os.path.exists('subdir1/.mellow3.txt'))
        self.assertTrue(os.path.exists('subdir1/.wild4.txt'))
        self.assertTrue(os.path.exists('subdir1/.DS_Store'))

        self.assertFalse(os.path.exists('subdir2/test_weird5.txt'))
        self.assertFalse(os.path.exists('subdir2/test_normal6.txt'))
        self.assertFalse(os.path.exists('subdir2/.test_weird5.txt'))
        self.assertFalse(os.path.exists('subdir2/.test_normal6.txt'))  
        self.assertTrue(os.path.exists('subdir2/weird5.txt'))
        self.assertTrue(os.path.exists('subdir2/normal6.txt'))      
        self.assertTrue(os.path.exists('subdir2/.weird5.txt'))
        self.assertTrue(os.path.exists('subdir2/.normal6.txt'))
        self.assertTrue(os.path.exists('subdir2/.DS_Store'))

        self.assertTrue(os.path.exists('subdir3/.DS_Store'))

        # Clean up the temporary directory
        os.chdir('..')
        shutil.rmtree(temp_directory)

if __name__ == '__main__':
    unittest.main()
