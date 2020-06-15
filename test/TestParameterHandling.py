"""
Testing key methods from Parameter Handling class
"""
from datetime import datetime
import os
from sources.tableau_hyper_management.FileOperations import FileOperations
from sources.tableau_hyper_management.ParameterHandling import ParameterHandling
import unittest


class TestParameterHandling(unittest.TestCase):

    def test_interpret_known_expression(self):
        class_fo = FileOperations()
        # load testing values from JSON file
        # where all cases are grouped
        json_structure = class_fo.fn_open_file_and_get_content(
            os.path.join(os.path.dirname(__file__),  'expressions.json'))
        # flatten out all testing values
        pair_values = []
        for crt_list in json_structure.values():
            pair_values += crt_list
        # parse through all pair of values and run the test
        class_ph = ParameterHandling()
        for current_pair in pair_values:
            reference_format = '%Y-%m-%d'
            if 'reference_format' in current_pair:
                reference_format = current_pair['reference_format']
            reference_date = datetime.strptime(current_pair['reference_value'], reference_format)
            expression_parts = current_pair['expression'].split('_')
            current_pair['start-iso-weekday'] = class_ph.set_default_starting_weekday({
                'session': current_pair,
                'query': current_pair,
                'sequence': current_pair,
            })
            value_to_assert = class_ph.interpret_known_expression(
                reference_date, expression_parts, current_pair['start-iso-weekday'])
            self.assertEqual(value_to_assert, current_pair['expected_value'],
                             'Provided value was "' + current_pair['reference_value']
                             + '", Expression was "' + current_pair['expression'] + '" '
                             + '", Expected was "' + current_pair['expected_value'] + '" '
                             + 'but received was "' + value_to_assert + '"...')


if __name__ == '__main__':
    unittest.main()

