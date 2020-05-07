"""
Data Manipulation class
"""
# package to add support for multi-language (i18n)
import gettext
# package to handle files/folders and related metadata/operations
import os


class DataManipulator:
    locale = None

    def __init__(self, in_language='en_US'):
        current_script = os.path.basename(__file__).replace('.py', '')
        lang_folder = os.path.join(os.path.dirname(__file__), current_script + '_Locale')
        self.locale = gettext.translation(current_script, lang_folder, languages=[in_language])

    def fn_add_and_shift_column(self, local_logger, timer, input_data_frame, input_details: list):
        evr = 'Empty Values Replacement'
        for crt_dict in input_details:
            timer.start()
            input_data_frame[crt_dict['New Column']] = input_data_frame[crt_dict['Original Column']]
            col_offset = self.fn_set_shifting_value(crt_dict)
            input_data_frame[crt_dict['New Column']] = \
                input_data_frame[crt_dict['New Column']].shift(col_offset)
            input_data_frame[crt_dict['New Column']] = \
                input_data_frame[crt_dict['New Column']].apply(lambda x: str(x)
                                                               .replace('nan', str(crt_dict[evr]))
                                                               .replace('.0', ''))
            local_logger.info(self.locale.gettext(
                'A new column named "{new_column_name}" as copy from "{original_column}" '
                + 'then shifted by {shifting_rows} to relevant data frame '
                + '(filling any empty value as {empty_values_replacement})')
                              .replace('{new_column_name}', crt_dict['New Column'])
                              .replace('{original_column}', crt_dict['Original Column'])
                              .replace('{shifting_rows}', str(col_offset))
                              .replace('{empty_values_replacement}',
                                       str(crt_dict['Empty Values Replacement'])))
            timer.stop()
        return input_data_frame

    @staticmethod
    def fn_add_minimum_and_maximum_columns_to_data_frame(input_data_frame, dict_expression):
        grouped_df = input_data_frame.groupby(dict_expression['group_by']) \
            .agg({dict_expression['calculation']: ['min', 'max']})
        grouped_df.columns = ['_'.join(col).strip() for col in grouped_df.columns.values]
        grouped_df = grouped_df.reset_index()
        if 'map' in dict_expression:
            grouped_df.rename(columns=dict_expression['map'], inplace=True)
        return grouped_df

    def fn_apply_query_to_data_frame(self, local_logger, timer, input_data_frame, extract_params):
        timer.start()
        query_expression = ''
        generic_pre_feedback = self.locale.gettext('Will retain only values {filter_type} '
                                                   + '"{filter_values}" within the field '
                                                   + '"{column_to_filter}"') \
            .replace('{column_to_filter}', extract_params['column_to_filter'])
        if extract_params['filter_to_apply'] == 'equal':
            local_logger.debug(generic_pre_feedback
                               .replace('{filter_type}', self.locale.gettext('equal with'))
                               .replace('{filter_values}', extract_params['filter_values']))
            query_expression = '`' + extract_params['column_to_filter'] + '` == "' \
                               + extract_params['filter_values'] + '"'
        elif extract_params['filter_to_apply'] == 'different':
            local_logger.debug(generic_pre_feedback
                               .replace('{filter_type}', self.locale.gettext('different than'))
                               .replace('{filter_values}', extract_params['filter_values']))
            query_expression = '`' + extract_params['column_to_filter'] + '` != "' \
                               + extract_params['filter_values'] + '"'
        elif extract_params['filter_to_apply'] == 'multiple_match':
            multiple_values = '["' + '", "'.join(extract_params['filter_values'].values()) + '"]'
            local_logger.debug(generic_pre_feedback
                               .replace('{filter_type}',
                                        self.locale.gettext('matching any of these values'))
                               .replace('{filter_values}', multiple_values))
            query_expression = '`' + extract_params['column_to_filter'] + '` in ' + multiple_values
        local_logger.debug(self.locale.gettext('Query expression to apply is: {query_expression}')
                           .replace('{query_expression}', query_expression))
        input_data_frame.query(query_expression, inplace=True)
        timer.stop()
        return input_data_frame

    def fn_filter_data_frame_by_index(self, local_logger, in_data_frame, filter_rule):
        reference_expression = filter_rule['Query Expression for Reference Index']
        index_current = in_data_frame.query(reference_expression, inplace=False)
        local_logger.info(self.locale.gettext(
            'Current index has been determined to be {index_current_value}')
                          .replace('{index_current_value}', str(index_current.index)))
        if str(index_current.index) != "Int64Index([], dtype='int64')" \
                and 'Deviation' in filter_rule:
            in_data_frame = self.fn_filter_data_frame_by_index_internal(local_logger, {
                'data frame': in_data_frame,
                'deviation': filter_rule['Deviation'],
                'index': index_current.index,
            })
        return in_data_frame

    def fn_filter_data_frame_by_index_internal(self, local_logger, in_dict):
        in_data_frame = in_dict['data_frame']
        for deviation_type in in_dict['deviation']:
            deviation_number = in_dict['deviation'][deviation_type]
            index_to_apply = in_dict['index']
            if deviation_type == 'Lower':
                index_to_apply -= deviation_number
                in_data_frame = in_data_frame[in_dict['index'] >= index_to_apply[0]]
            elif deviation_type == 'Upper':
                index_to_apply += deviation_number
                in_data_frame = in_data_frame[in_dict['index'] <= index_to_apply[0]]
            local_logger.info(self.locale.gettext(
                '{deviation_type} Deviation Number is {deviation_number} '
                + 'to be applied to Current index, became {index_to_apply}')
                              .replace('{deviation_type}', deviation_type)
                              .replace('{deviation_number}', str(deviation_number))
                              .replace('{index_to_apply}', str(index_to_apply)))
        return in_dict['data_frame']

    @staticmethod
    def fn_get_column_index_from_data_frame(data_frame_columns, column_name_to_identify):
        column_index_to_return = 0
        for ndx, column_name in enumerate(data_frame_columns):
            if column_name == column_name_to_identify:
                column_index_to_return = ndx
        return column_index_to_return

    @staticmethod
    def fn_get_first_and_last_column_value_from_data_frame(in_data_frame, in_column_name):
        return {
            'first': in_data_frame.iloc[0][in_column_name],
            'last': in_data_frame.iloc[(len(in_data_frame) - 1)][in_column_name],
        }

    @staticmethod
    def fn_set_shifting_value(in_dict):
        offset_sign = 1
        if in_dict['Direction'] == 'up':
            offset_sign = -1
        return offset_sign * in_dict['Deviation']
