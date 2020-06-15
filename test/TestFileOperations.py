from datetime import datetime
import os
from db_extractor.LoggingNeeds import LoggingNeeds
from db_extractor.FileOperations import FileOperations
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
                                 .replace('test', 'sources/project_locale'),
                                 'localizations_compile.py'))

    def test_file_statistics(self):
        class_fo = FileOperations()
        value_to_assert = class_fo.fn_get_file_statistics({'file name': __file__})['size [bytes]']
        value_to_compare_with = os.path.getsize(__file__)
        self.assertEqual(value_to_assert, value_to_compare_with)

    def test_file_dates(self):
        class_fo = FileOperations()
        value_to_assert = class_fo.fn_get_file_dates(__file__)['created']
        value_to_compare_with = datetime.fromtimestamp(os.path.getctime(__file__))
        self.assertEqual(value_to_assert, value_to_compare_with)

    def test_file_verdict(self):
        class_ln = LoggingNeeds()
        class_ln.initiate_logger('None', __file__)
        class_fo = FileOperations()
        ref_datetime = os.path.getctime(__file__)
        relevant_file = os.path.join(
            os.path.dirname(__file__).replace('test', 'sources'), 'project_locale/__init__.py')
        value_to_assert = class_fo.fn_get_file_datetime_verdict(
            class_ln.logger, relevant_file, 'created', ref_datetime)
        self.assertEqual(value_to_assert, class_fo.locale.gettext('older'))
