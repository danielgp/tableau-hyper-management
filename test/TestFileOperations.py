from datetime import datetime
import os
from sources.common.FileOperations import FileOperations
import unittest
# package to facilitate multiple operation system operations
import platform


class TestFileOperations(unittest.TestCase):

    def setUp(self) -> None:
        python_binary = 'python'
        if platform.system() == 'Windows':
            python_binary += '.exe'
        os.system(python_binary + ' '
                  + os.path.join(os.path.normpath(os.path.dirname(__file__))
                                 .replace('test', 'sources'), 'localizations_compile.py'))

    def test_file_statistics(self):
        class_fo = FileOperations()
        value_to_assert = class_fo.fn_get_file_statistics(__file__)['size [bytes]']
        value_to_compare_with = os.path.getsize(__file__)
        self.assertEqual(value_to_assert, value_to_compare_with)

    def test_file_dates(self):
        class_fo = FileOperations()
        value_to_assert = class_fo.fn_get_file_dates(__file__)['created']
        value_to_compare_with = datetime.fromtimestamp(os.path.getctime(__file__))
        self.assertEqual(value_to_assert, value_to_compare_with)
