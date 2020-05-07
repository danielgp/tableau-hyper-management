"""
Data Input Output class
"""
# package to add support for multi-language (i18n)
import gettext
# package to handle files/folders and related metadata/operations
import os
# package facilitating Data Frames manipulation
import pandas


class DataInputOutput:
    locale = None

    def __init__(self, in_language='en_US'):
        current_script = os.path.basename(__file__).replace('.py', '')
        lang_folder = os.path.join(os.path.dirname(__file__), current_script + '_Locale')
        self.locale = gettext.translation(current_script, lang_folder, languages=[in_language])

    @staticmethod
    def fn_add_missing_defaults_to_dict_message(in_dict):
        if 'field delimiter' not in in_dict:
            in_dict['field delimiter'] = os.pathsep
        if 'compression' not in in_dict:
            in_dict['compression'] = 'infer'
        return in_dict

    def fn_build_feedback_for_logger(self, operation_details):
        messages = {}
        if operation_details['operation'] == 'load':
            files_counted = str(operation_details['files counted'])
            messages = {
                'failed': self.locale.gettext(
                    'Error encountered on loading Pandas Data Frame '
                    + 'from {file_type} file type (see below)')
                    .replace('{file_type}',  operation_details['format'].upper()),
                'success': self.locale.gettext(
                    'All {files_counted} files of type {file_type} '
                    + 'successfully added to a Pandas Data Frame')
                    .replace('{files_counted}', files_counted)
                    .replace('{file_type}', operation_details['format'].upper())
            }
        elif operation_details['operation'] == 'save':
            messages = {
                'failed': self.locale.gettext(
                    'Error encountered on saving Pandas Data Frame '
                    + 'into a {file_type} file type (see below)')
                    .replace('{file_type}',  operation_details['format'].upper()),
                'success': self.locale.gettext(
                    'Pandas Data Frame has just been saved to file "{file_name}", '
                    + 'considering {file_type} as file type')
                    .replace('{file_name}',operation_details['name'])
                    .replace('{file_type}',  operation_details['format'].upper()),
            }
        return messages

    def fn_file_operation_logger(self, local_logger, in_logger_dict):
        messages = self.fn_build_feedback_for_logger(in_logger_dict)
        if in_logger_dict['error details'] is None:
            local_logger.info(messages['success'])
        else:
            local_logger.error(messages['failed'])
            local_logger.error(in_logger_dict['error details'])

    def fn_load_file_into_data_frame(self, in_logger, timer, in_dict):
        timer.start()
        if self.fn_store_data_frame_to_file_validation(in_logger, in_dict):
            in_dict = self.fn_add_missing_defaults_to_dict_message(in_dict)
            in_dict.update({'operation': 'load'})
            in_dict = self.fn_pack_dict_message(in_dict, in_dict['file list'])
            in_dict = self.fn_internal_load_csv_file_into_data_frame(in_dict)
            in_dict = self.fn_internal_load_excel_file_into_data_frame(in_dict)
            in_dict = self.fn_internal_load_json_file_into_data_frame(in_dict)
            in_dict = self.fn_internal_load_pickle_file_into_data_frame(in_dict)
            self.fn_file_operation_logger(in_logger, in_dict)
        timer.stop()
        return in_dict['out data frame']

    @staticmethod
    def fn_internal_load_csv_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'csv':
            try:
                in_dict['out data frame'] = pandas.concat(
                    [pandas.read_csv(filepath_or_buffer=crt_file,
                                     delimiter=in_dict['field delimiter'],
                                     cache_dates=True,
                                     index_col=None,
                                     memory_map=True,
                                     low_memory=False,
                                     encoding='utf-8',
                                     ) for crt_file in in_dict['files list']])
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_excel_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'excel':
            try:
                in_dict['out data frame'] = pandas.concat(
                    [pandas.read_excel(io=crt_file,
                                       verbose=True,
                                       ) for crt_file in in_dict['files list']])
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_json_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'json':
            try:
                in_dict['out data frame'] = pandas.concat(
                    [pandas.read_json(filepath_or_buffer=crt_file,
                                      compression=in_dict['compression'],
                                      ) for crt_file in in_dict['files list']])
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_pickle_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'pickle':
            try:
                in_dict['out data frame'] = pandas.concat(
                    [pandas.read_pickle(filepath_or_buffer=crt_file,
                                        compression=in_dict['compression'],
                                        ) for crt_file in in_dict['files list']])
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_store_data_frame_to_csv_file(in_dict):
        if in_dict['format'].lower() == 'csv':
            try:
                in_dict['in data frame'].to_csv(path_or_buf=in_dict['name'],
                                                sep=in_dict['field delimiter'],
                                                header=True,
                                                index=False,
                                                encoding='utf-8')
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_store_data_frame_to_excel_file(in_dict):
        if in_dict['format'].lower() == 'excel':
            try:
                in_dict['in data frame'].to_excel(excel_writer=in_dict['name'],
                                                  engine='xlsxwriter',
                                                  freeze_panes=(1, 1),
                                                  encoding='utf-8',
                                                  index=False,
                                                  verbose=True)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_store_data_frame_to_json_file(in_dict):
        if in_dict['format'].lower() == 'json':
            try:
                in_dict['in data frame'].to_json(path_or_buf=in_dict['name'],
                                                 compression=in_dict['compression'])
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_store_data_frame_to_pickle_file(in_dict):
        if in_dict['format'].lower() == 'pickle':
            try:
                in_dict['in data frame'].to_pickle(path=in_dict['name'],
                                                   compression=in_dict['compression'])
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_pack_dict_message(in_dict, in_file_list):
        return {
            'compression': in_dict['compression'],
            'field delimiter': in_dict['field delimiter'],
            'files list': in_file_list,
            'files counted': len(in_file_list),
            'error details': None,
            'format': in_dict['format'],
            'name': in_dict['name'],
            'in data frame': None,
            'operation': in_dict['operation'],
            'out data frame': None,
        }

    def fn_store_data_frame_to_file(self, in_logger, timer, in_data_frame, in_dict):
        timer.start()
        if self.fn_store_data_frame_to_file_validation(in_logger, in_dict):
            in_dict = self.fn_add_missing_defaults_to_dict_message(in_dict)
            in_dict.update({'operation': 'save'})
            in_dict = self.fn_pack_dict_message(in_dict, [])
            in_dict.update({'in data frame': in_data_frame})
            in_dict = self.fn_internal_store_data_frame_to_csv_file(in_dict)
            in_dict = self.fn_internal_store_data_frame_to_excel_file(in_dict)
            in_dict = self.fn_internal_store_data_frame_to_json_file(in_dict)
            in_dict = self.fn_internal_store_data_frame_to_pickle_file(in_dict)
            self.fn_file_operation_logger(in_logger, in_dict)
        timer.stop()

    def fn_store_data_frame_to_file_validation(self, local_logger, in_file_details):
        given_format_is_implemented = False
        if 'format' in in_file_details:
            implemented_file_formats = ['csv', 'excel', 'json', 'pickle']
            given_format = in_file_details['format'].lower()
            given_format_is_implemented = True
            if given_format not in implemented_file_formats:
                given_format_is_implemented = False
                local_logger.error(self.locale.gettext(
                    'File "format" attribute has a value of "{format_value}" '
                    + 'which is not among currently implemented values: '
                    + '"{implemented_file_formats}", '
                    + 'therefore desired file operation is not possible')
                                   .replace('{format_value}', given_format)
                                   .replace('{implemented_file_formats}',
                                            '", "'.join(implemented_file_formats)))
        else:
            local_logger.error(self.locale.gettext(
                    'File "format" attribute is mandatory in the file setting, but missing, '
                    + 'therefore desired file operation is not possible'))
        return given_format_is_implemented
