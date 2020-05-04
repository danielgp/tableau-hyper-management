"""
TypeDetermination - a data type determination library

This library allows data type determination based on data frame content
"""
# regular expression package
import re
# package to handle numerical structures
import numpy as np
# package to facilitate common operations
from common.BasicNeeds import BasicNeeds


class TypeDetermination:
    class_bn = None

    def __init__(self):
        self.class_bn = BasicNeeds()

    def fn_analyze_field_content_to_establish_data_type(self, logger, field_characteristics,
                                                        data_types):
        crt_field_type = self.fn_type_determination(
                field_characteristics['unique_values'][0], data_types)
        # since date fields are not accepted to have ny null value by Tableau Hyper API
        # following forced String type is enforced
        if crt_field_type[:4] == 'date' and field_characteristics['nulls'] != 0:
            crt_field_type = 'str'
        # write aside the determined value
        field_dict = {
            'order': field_characteristics['order'],
            'name': field_characteristics['name'],
            'nulls': field_characteristics['nulls'],
            'panda_type': field_characteristics['panda_type'],
            'type': crt_field_type,
            'type_index': list(data_types.keys()).index(crt_field_type)
        }
        logger.debug('Column ' + str(field_characteristics['order'])
                     + ' having the name [' + field_characteristics['name'] + '] has the value <'
                     + str(field_characteristics['unique_values'][0])
                     + f'> which mean is of type "{crt_field_type}"')
        if crt_field_type == 'str':
            return field_dict
        else:
            return self.fn_analyze_sample(logger, field_characteristics, field_dict, data_types)

    def fn_analyze_sample(self, logger, field_characteristics, field_structure, data_types):
        # Analyze unique values
        for unique_row_index, current_value in enumerate(field_characteristics['unique_values']):
            # determine the field type by current content
            crt_field_type = self.fn_type_determination(current_value, data_types)
            crt_type_index = list(data_types.keys()).index(crt_field_type)
            # is the current type is more important?
            if crt_type_index > field_structure['type_index']:
                logger.debug('Column ' + str(field_characteristics['order']) + ' having the name ['
                             + field_characteristics['name'] + f'] has the value <{current_value}> '
                             + f'which means is of type "{crt_field_type}" '
                             + 'and this is stronger than previously thought '
                             + 'to be as "' + field_structure['type'] + '"')
                field_structure['type'] = crt_field_type
                field_structure['type_index'] = crt_type_index
            # If currently determined field type is string makes not sense to scan any further
            if crt_field_type == 'str':
                return field_structure
        return field_structure

    def fn_detect_csv_structure(self, logger, input_csv_data_frame, input_parameters, data_types):
        col_idx = 0
        csv_structure = []
        # Cycle through all found columns
        for label, content in input_csv_data_frame.items():
            panda_determined_type = content.infer_objects().dtypes
            counted_nulls = content.isnull().sum()
            logger.debug(f'Field "{label}" according to Pandas package '
                         + f'is of type "{panda_determined_type}" '
                         + f'with {counted_nulls} counted NULLs')
            if panda_determined_type in ('float64', 'object'):
                list_unique_values = self.fn_unique_values_isolation(
                        logger, label, content, panda_determined_type, input_parameters)
                unique_v_list = {
                    'order': col_idx,
                    'name': label,
                    'nulls': counted_nulls,
                    'panda_type': panda_determined_type,
                    'unique_values': list_unique_values
                }
                logger.debug('parameters used for further data analysis are: '
                             + self.class_bn.fn_multi_line_string_to_single(str(unique_v_list)))
                csv_structure.append(col_idx)
                csv_structure[col_idx] = \
                    self.fn_analyze_field_content_to_establish_data_type(
                            logger, unique_v_list, data_types)
            elif panda_determined_type in ('bool', 'int64'):
                csv_structure.append(col_idx)
                csv_structure[col_idx] = {
                    'order': col_idx,
                    'name': label,
                    'nulls': counted_nulls,
                    'panda_type': panda_determined_type,
                    'type': str(panda_determined_type).replace('64', ''),
                }
            col_idx += 1
        return csv_structure

    @staticmethod
    def fn_type_determination(input_variable_to_assess, data_types):
        # Website https://regex101.com/ was used to validate below code
        variable_to_assess = str(input_variable_to_assess)
        if variable_to_assess == '':
            return 'empty'
        else:
            for current_data_type, current_format in data_types.items():
                if re.match(current_format, variable_to_assess):
                    return current_data_type
            return 'str'

    def fn_unique_values_isolation(self, logger, label, content, panda_determined_type, in_prmtrs):
        counted_values_not_null = content.notnull().sum()
        counted_values_unique = content.nunique()
        content = content.dropna()
        if panda_determined_type == 'float64':
            content = content.apply(lambda x: x if (int(x) != x) else int(x))
        list_unique_values = content.unique()[0:int(in_prmtrs.unique_values_to_analyze_limit)]
        compact_unique_values = \
            self.class_bn.fn_multi_line_string_to_single(
                    '>, <'.join(np.array(list_unique_values, dtype=str)))
        logger.debug(f'additional characteristics for the field "{label}" are: ' +
                     f'count of not-null values: {counted_values_not_null}, ' +
                     f'count of unique values: {counted_values_unique}, ' +
                     f'list of not-null and unique values is: <' + compact_unique_values + '>')
        return list_unique_values
