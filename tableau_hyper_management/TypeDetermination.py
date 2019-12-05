"""
TypeDetermination - a data type determination library

This library allows data type determination based on data frame content
"""

import numpy as np
import re

from . import BasicNeeds as ClassBN


class TypeDetermination:

    def fn_analyze_field_content_to_establish_data_type(self,
                                                        field_idx, 
                                                        field_name,
                                                        field_counted_nulls,
                                                        field_unique_values,
                                                        field_panda_type,
                                                        data_type_and_their_formats_to_evaluate,
                                                        verbose):
        field_structure = []
        # Analyze unique values
        for unique_row_index, current_value in enumerate(field_unique_values):
            # determine the field type by current content
            crt_field_type = self.fn_type_determination(current_value,
                                                        data_type_and_their_formats_to_evaluate)
            # write aside the determined value
            if unique_row_index == 0:
                field_structure = {
                    'order': field_idx,
                    'name': field_name,
                    'nulls': field_counted_nulls,
                    'panda_type': field_panda_type,
                    'type': crt_field_type
                }
                ClassBN.fn_optional_print(verbose,
                                          f'Column {field_idx} having the name [{field_name}] '
                                          + f'has the value <{current_value}> '
                                          + f'which mean is of type "{crt_field_type}"')
            else:
                crt_type_index = list(data_type_and_their_formats_to_evaluate.keys()).\
                    index(crt_field_type)
                prv_type = field_structure['type']
                prv_type_index = list(data_type_and_their_formats_to_evaluate.keys()).\
                    index(prv_type)
                # if CSV structure for current field (column) exists,
                # does the current type is more important?
                if crt_type_index > prv_type_index:
                    ClassBN.fn_optional_print(verbose,
                                              f' column {field_idx} having the name [{field_name}] '
                                              + f'has the value <{current_value}> '
                                              + f'which means is of type "{crt_field_type}" '
                                              + 'and this is stronger than previously thought '
                                              + f'to be as "{prv_type}"')
                    field_structure['type'] = crt_field_type
            # If currently determined field type is string makes not sense to scan any further
            if crt_field_type == 'str':
                return field_structure
        return field_structure

    @staticmethod
    def fn_detect_csv_structure(self, input_csv_data_frame, formats_to_evaluate, verbose):
        col_idx = 0
        csv_structure = []
        # Cycle through all found columns
        for label, content in input_csv_data_frame.items():
            panda_determined_type = content.infer_objects().dtypes
            ClassBN.fn_optional_print(verbose, f'Field "{label}" according to Pandas package '
                                      + f'is of type "{panda_determined_type}"')
            counted_nulls = content.isnull().sum()
            if panda_determined_type in ('float64', 'object'):
                list_unique_vals = content.dropna().unique()
                self.fn_optional_column_statistics(self, verbose, label, content, list_unique_vals)
                csv_structure.append(col_idx)
                csv_structure[col_idx] = self.\
                    fn_analyze_field_content_to_establish_data_type(self,
                                                                    col_idx,
                                                                    label,
                                                                    counted_nulls,
                                                                    list_unique_vals[0:200],
                                                                    panda_determined_type,
                                                                    formats_to_evaluate,
                                                                    verbose)
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
    def fn_optional_column_statistics(self, verbose, field_name, field_content, field_unique_vals):
        if verbose:
            counted_values_null = field_content.isnull().sum()
            counted_values_not_null = field_content.notnull().sum()
            counted_values_unique = field_content.nunique()
            ClassBN.fn_optional_print(verbose, f'"{field_name}" has following characteristics: ' +
                                     f'count of null values: {counted_values_null}, ' +
                                     f'count of not-null values: {counted_values_not_null}, ' +
                                     f'count of unique values: {counted_values_unique}, ' +
                                     f'list of not-null and unique values is: <' +
                                     '>, <'.join(np.array(field_unique_vals, dtype=str)) + '>')

    @staticmethod
    def fn_type_determination(intput_variable_to_assess, evaluation_formats):
        # Website https://regex101.com/ was used to validate below code
        variable_to_assess = str(intput_variable_to_assess)
        if variable_to_assess == '':
            return 'empty'
        else:
            for current_dtype, current_format in evaluation_formats.items():
                if re.match(current_format, variable_to_assess):
                    return current_dtype
            return 'str'
