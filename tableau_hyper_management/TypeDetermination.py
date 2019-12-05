"""
TypeDetermination - a data type determination library

This library allows data type determination based on data frame content
"""
# standard Python packages
import re
# additional Python packages available from PyPi
import numpy as np
# Custom class specific to this package
from .BasicNeeds import BasicNeeds as ClassBN


class TypeDetermination:

    def fn_analyze_field_content_to_establish_data_type(self,
                                                        field_characteristics,
                                                        known_formats,
                                                        verbose):
        field_structure = []
        # Analyze unique values
        for unique_row_index, current_value in enumerate(field_characteristics['unique_values']):
            # determine the field type by current content
            crt_field_type = self.fn_type_determination(current_value,
                                                        known_formats)
            # write aside the determined value
            if unique_row_index == 0:
                field_structure = {
                    'order': field_characteristics['order'],
                    'name': field_characteristics['name'],
                    'nulls': field_characteristics['nulls'],
                    'panda_type': field_characteristics['panda_type'],
                    'type': crt_field_type,
                    'type_index': list(known_formats.keys()).index(crt_field_type)
                }
                ClassBN.fn_optional_print(ClassBN, verbose,
                                          'Column ' + str(field_characteristics['order'])
                                          + ' having the name ['
                                          + field_characteristics['name']
                                          + f'] has the value <{current_value}>'
                                          + f'which mean is of type "{crt_field_type}"')
            else:
                crt_type_index = list(known_formats.keys()).index(crt_field_type)
                # if CSV structure for current field (column) exists,
                # does the current type is more important?
                if crt_type_index > field_structure['type_index']:
                    ClassBN.fn_optional_print(ClassBN, verbose,
                                              'Column ' + str(field_characteristics['order'])
                                              + ' having the name ['
                                              + field_characteristics['name']
                                              + f'] has the value <{current_value}> '
                                              + f'which means is of type "{crt_field_type}" '
                                              + 'and this is stronger than previously thought '
                                              + 'to be as "' + field_structure['type'] + '}"')
                    field_structure['type'] = crt_field_type
                    field_structure['type_index'] = crt_type_index
            # If currently determined field type is string makes not sense to scan any further
            if crt_field_type == 'str':
                return field_structure
        return field_structure

    def fn_detect_csv_structure(self, input_csv_data_frame, formats_to_evaluate, in_prmtrs):
        col_idx = 0
        csv_structure = []
        # Cycle through all found columns
        for label, content in input_csv_data_frame.items():
            panda_determined_type = content.infer_objects().dtypes
            ClassBN.fn_optional_print(ClassBN, in_prmtrs.verbose,
                                      f'Field "{label}" according to Pandas package '
                                      + f'is of type "{panda_determined_type}"')
            counted_nulls = content.isnull().sum()
            if panda_determined_type in ('float64', 'object'):
                list_unique_values = content.dropna().unique()
                self.fn_optional_column_statistics(in_prmtrs.verbose, label, content,
                                                   list_unique_values)
                preliminary_list = {
                    'order': col_idx,
                    'name': label,
                    'nulls': counted_nulls,
                    'panda_type': panda_determined_type,
                    'unique_values': list_unique_values[0:in_prmtrs.unique_values_to_analyze_limit]
                }
                csv_structure.append(col_idx)
                csv_structure[col_idx] = self.\
                    fn_analyze_field_content_to_establish_data_type(self, preliminary_list,
                                                                    formats_to_evaluate,
                                                                    in_prmtrs.verbose)
            elif panda_determined_type == 'int64':
                csv_structure.append(col_idx)
                csv_structure[col_idx] = {
                    'order': col_idx,
                    'name': label,
                    'nulls': counted_nulls,
                    'panda_type': panda_determined_type,
                    'type': 'int'
                }
            col_idx += 1
        return csv_structure

    @staticmethod
    def fn_optional_column_statistics(verbose, field_name, field_content, field_unique_values):
        if verbose:
            counted_values_null = field_content.isnull().sum()
            counted_values_not_null = field_content.notnull().sum()
            counted_values_unique = field_content.nunique()
            ClassBN.fn_optional_print(verbose, f'"{field_name}" has following characteristics: ' +
                                      f'count of null values: {counted_values_null}, ' +
                                      f'count of not-null values: {counted_values_not_null}, ' +
                                      f'count of unique values: {counted_values_unique}, ' +
                                      f'list of not-null and unique values is: <' +
                                      '>, <'.join(np.array(field_unique_values, dtype=str)) + '>')

    @staticmethod
    def fn_type_determination(input_variable_to_assess, evaluation_formats):
        # Website https://regex101.com/ was used to validate below code
        variable_to_assess = str(input_variable_to_assess)
        if variable_to_assess == '':
            return 'empty'
        else:
            for current_data_type, current_format in evaluation_formats.items():
                if re.match(current_format, variable_to_assess):
                    return current_data_type
            return 'str'
