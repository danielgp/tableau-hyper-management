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

    @staticmethod
    def fn_additional_column_statistics(logger, field_name, field_content, field_unique_values):
        counted_values_not_null = field_content.notnull().sum()
        counted_values_unique = field_content.nunique()
        logger.debug(f'additional characteristics for the field "{field_name}" are: ' +
                     f'count of not-null values: {counted_values_not_null}, ' +
                     f'count of unique values: {counted_values_unique}, ' +
                     f'list of not-null and unique values is: <' +
                     '>, <'.join(np.array(field_unique_values, dtype=str)) + '>')

    def fn_analyze_field_content_to_establish_data_type(self, logger, field_characteristics):
        crt_field_type = self.fn_type_determination(field_characteristics['unique_values'][0])
        # write aside the determined value
        field_structure = {
            'order'     : field_characteristics['order'],
            'name'      : field_characteristics['name'],
            'nulls'     : field_characteristics['nulls'],
            'panda_type': field_characteristics['panda_type'],
            'type'      : crt_field_type,
            'type_index': list(ClassBN.cfg_dtls['data_types'].keys()).index(crt_field_type)
        }
        logger.debug('Column ' + str(field_characteristics['order'])
                     + ' having the name [' + field_characteristics['name'] + '] has the value <'
                     + str(field_characteristics['unique_values'][0])
                     + f'> which mean is of type "{crt_field_type}"')
        if crt_field_type == 'str':
            return field_structure
        return self.fn_analyze_sample(self, logger, field_characteristics, field_structure)

    def fn_analyze_sample(self, logger, field_characteristics, field_structure):
        # Analyze unique values
        for unique_row_index, current_value in enumerate(field_characteristics['unique_values']):
            # determine the field type by current content
            crt_field_type = self.fn_type_determination(current_value)
            crt_type_index = list(ClassBN.cfg_dtls['data_types'].keys()).index(crt_field_type)
            # is the current type is more important?
            if crt_type_index > field_structure['type_index']:
                logger.debug('Column ' + str(field_characteristics['order']) + ' having the name ['
                             + field_characteristics['name'] + f'] has the value <{current_value}> '
                             + f'which means is of type "{crt_field_type}" '
                             + 'and this is stronger than previously thought '
                             + 'to be as "' + field_structure['type'] + '}"')
                field_structure['type'] = crt_field_type
                field_structure['type_index'] = crt_type_index
            # If currently determined field type is string makes not sense to scan any further
            if crt_field_type == 'str':
                return field_structure
        return field_structure

    def fn_detect_csv_structure(self, logger, input_csv_data_frame, in_prmtrs):
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
                if panda_determined_type == 'float64':
                    content = content.apply(lambda x: x if (int(x) != x) else int(x))
                list_unique_values = content.dropna().unique()
                self.fn_additional_column_statistics(logger, label, content,
                                                     list_unique_values)
                preliminary_list = {
                    'order':            col_idx,
                    'name':             label,
                    'nulls':            counted_nulls,
                    'panda_type':       panda_determined_type,
                    'unique_values':    list_unique_values[0:in_prmtrs.unique_values_to_analyze_limit]
                }
                logger.debug('parameters used for further data analysis are: '
                             + str(preliminary_list).replace(chr(10), ''))
                csv_structure.append(col_idx)
                csv_structure[col_idx] = self.\
                    fn_analyze_field_content_to_establish_data_type(self, logger,
                                                                    preliminary_list)
            elif panda_determined_type in ('bool', 'int64'):
                csv_structure.append(col_idx)
                csv_structure[col_idx] = {
                    'order':        col_idx,
                    'name':         label,
                    'nulls':        counted_nulls,
                    'panda_type':   panda_determined_type,
                    'type':         str(panda_determined_type).replace('64', ''),
                }
            col_idx += 1
            logger.debug(str(csv_structure).replace(chr(10), ''))
        return csv_structure

    @staticmethod
    def fn_type_determination(input_variable_to_assess):
        # Website https://regex101.com/ was used to validate below code
        variable_to_assess = str(input_variable_to_assess)
        if variable_to_assess == '':
            return 'empty'
        else:
            for current_data_type, current_format in ClassBN.cfg_dtls['data_types'].items():
                if re.match(current_format, variable_to_assess):
                    return current_data_type
            return 'str'
