"""
Common constants and functions used by multiple tests.
"""
import os
import shutil
import unittest

PYGOUNT_PROJECT_FOLDER = os.path.dirname(os.path.dirname(__file__))
PYGOUNT_SOURCE_FOLDER = os.path.join(PYGOUNT_PROJECT_FOLDER, "pygount")


class TempFolderTest(unittest.TestCase):
    def setUp(self):
        self.tests_temp_folder = os.path.join(PYGOUNT_PROJECT_FOLDER, "tests", ".temp")
        os.makedirs(self.tests_temp_folder, exist_ok=True)

    def create_temp_file(self, relative_target_path, content):
        result = os.path.join(self.tests_temp_folder, relative_target_path)
        with open(result, "w", encoding="utf-8") as target_file:
            target_file.write(content)
        return result

    def tearDown(self):
        shutil.rmtree(self.tests_temp_folder)
