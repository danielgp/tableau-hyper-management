import csv
import numpy as np
import pandas as pd
import re
import sys

from BasicNeeds import BasicNeeds as cls_bn


class TypeDetermination:

    importance__low_to_high = [
        'empty',
        'int',
        'float-USA',
        'date-iso8601',
        'date-USA',
        'time-24',
        'time-24-us',
        'time-USA',
        'time-USA-us',
        'datetime-iso8601',
        'datetime-iso8601-us',
        'str'
    ]

    @staticmethod
    def fn_analyze_field_content_to_establish_data_type(self, 
                                                        verbose, 
                                                        field_idx, 
                                                        field_name, 
                                                        field_counted_nulls,
                                                        field_unique_values):
        # Analyze unique values
        for unique_row_index, current_value in enumerate(field_unique_values):
            # determine the field type by current contentfn_analyze_field_content_to_establish_data_type
            crt_field_type = self.fn_type_determination(current_value)
            # wrise aside the determined value
            if unique_row_index == 0:
                field_structure = {
                    'order': field_idx,
                    'name': field_name,
                    'nulls': field_counted_nulls,
                    'type': crt_field_type
                }
                cls_bn.fn_optional_print(cls_bn, verbose, f'Column {field_idx} having the name [{field_name}] '
                                         + f'has the value <{current_value}> which mean is of type "{crt_field_type}"')
            else:
                crt_type_index = self.importance__low_to_high.index(crt_field_type)
                prv_type = field_structure['type']
                prv_type_index = self.importance__low_to_high.index(prv_type)
                # if CSV structure for current field (column) exists, does the current type is more important?
                if crt_type_index > prv_type_index:
                    cls_bn.fn_optional_print(cls_bn, verbose, f' column {field_idx} having the name [{field_name}] '
                                             + f'has the value <{current_value}> '
                                             + f'which means is of type "{crt_field_type}" '
                                             + 'and this is stronger than previously thought to be '
                                             + f'as "{prv_type}"')
                    field_structure['type'] = crt_field_type
            # If currently determined field type is string makes not sense to scan any further
            if crt_field_type == 'str':
                return field_structure
        return field_structure

    def fn_detect_csv_structure(self, given_file_name, csv_field_separator, verbose):
        # Import the data
        csv_content_df = pd.read_csv(filepath_or_buffer=given_file_name,
                                     delimiter = csv_field_separator,
                                     cache_dates = True,
                                     #keep_default_na = False,
                                     encoding = 'utf-8')
        col_idx = 0
        csv_structure = []
        # Cycle through all found columns
        for label, content in csv_content_df.items():
            panda_determined_type = content.infer_objects().dtypes
            cls_bn.fn_optional_print(cls_bn, verbose, f'Field "{label}" according to Pandas package '
                                     + f'is of type "{panda_determined_type}"')
            counted_nulls = content.isnull().sum()
            if panda_determined_type in ('float64', 'object'):
                list_unique_values = content.dropna().unique()
                self.fn_optional_column_statistics(self, verbose, label, content, list_unique_values)
                csv_structure.append(col_idx)
                csv_structure[col_idx] = self.fn_analyze_field_content_to_establish_data_type(self,
                                                                                              verbose,
                                                                                              col_idx,
                                                                                              label,
                                                                                              counted_nulls,
                                                                                              list_unique_values[0:200])
            elif panda_determined_type == 'int64':
                csv_structure.append(col_idx)
                csv_structure[col_idx] = {
                    'order': col_idx,
                    'name': label,
                    'nulls': counted_nulls,
                    'type': 'int'
                }
            col_idx += 1
        return csv_structure

    @staticmethod
    def fn_optional_column_statistics(self, verbose, field_name, field_content, field_unique_values):
        if verbose:
            counted_values_null = field_content.isnull().sum()
            counted_values_not_null = field_content.notnull().sum()
            counted_values_unique = field_content.nunique()
            cls_bn.fn_optional_print(cls_bn, verbose, f'"{field_name}" has following characteristics: ' + \
                                     f'count of null values: {counted_values_null}, ' + \
                                     f'count of not-null values: {counted_values_not_null}, ' + \
                                     f'count of unique values: {counted_values_unique}, ' + \
                                     f'list of not-null and unique values is: <' + \
                                     '>, <'.join(np.array(field_unique_values, dtype=str)) + '>')

    @staticmethod
    def fn_type_determination(intput_variable_to_assess):
        # Website https://regex101.com/ was used to validate below code
        re_int = '^[+-]*[0-9]+(\\.{1}0*)*$' # final "." or ".0" is still considered as integer
        re_float_usa = '^[+-]*[0-9]*\\.{1}[0-9]*$'
        re_date_us = '^([1-9]|11|12|0[0-9]|1[0-2])/([1-9]|0[0-9]|1[0-9]|2[0-9]|3[0-1])/(1[0-9]{3}|2[0-9]{3})$'
        re_date_iso8601 = '^(1[0-9]{3}|2[0-9]{3})-([0-9]|0[0-9]|1[0-2])-([0-9]|0[0-9]|1[0-9]|2[0-9]|3[0-1])$'
        re_time24 = '^(2[0-3]|[01][0-9]|[0-9]):([0-5][0-9]|[0-9]):([0-5][0-9]|[0-9])$'
        re_time_us = '^([0-9]|0[0-9]|1[0-2]):{1}([0-5][0-9]|[0-9]):{1}([0-5][0-9]|[0-9])\\s*(AM|am|PM|pm)$'
        variable_to_assess = str(intput_variable_to_assess)
        if variable_to_assess == '':
            return 'empty'
        elif re.match(re_int, variable_to_assess):
            return 'int'
        elif re.match(re_float_usa, variable_to_assess):
            return 'float-USA'
        elif re.match(re_date_iso8601, variable_to_assess):
            return 'date-iso8601'
        elif re.match(re_date_us, variable_to_assess):
            return 'date-USA'
        elif re.match(re_time24, variable_to_assess):
            return 'time-24'
        elif re.match(re_time24.replace(')$', ').([0-9]{6})$'), variable_to_assess):
            return 'time-24-us'
        elif re.match(re_time_us, variable_to_assess):
            return 'time-USA'
        elif re.match(re_time_us.replace(')$', ').([0-9]{6})$'), variable_to_assess):
            return 'time-USA-us'
        elif re.match(re_date_iso8601[:-1] + ' ' + re_time24[1:], variable_to_assess):
            return 'datetime-iso8601'
        elif re.match(re_date_iso8601[:-1] + ' ' + re_time24[1:].replace(')$', ').([0-9]{6})$'), variable_to_assess):
            return 'datetime-iso8601-us'
        else:
            return 'str'
