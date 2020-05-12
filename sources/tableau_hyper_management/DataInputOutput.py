"""
Data Input Output class
"""
# package to add support for multi-language (i18n)
import gettext
# package to handle files/folders and related metadata/operations
import os

# local packages
from .DataDiskRead import DataDiskRead
from .DataDiskWrite import DataDiskWrite


class DataInputOutput(DataDiskRead, DataDiskWrite):
    locale = None

    def __init__(self, in_language):
        file_parts = os.path.normpath(os.path.abspath(__file__)).replace('\\', os.path.altsep) \
            .split(os.path.altsep)
        locale_domain = file_parts[(len(file_parts) - 1)].replace('.py', '')
        locale_folder = os.path.normpath(os.path.join(
                os.path.join(os.path.altsep.join(file_parts[:-2]), 'project_locale'),
                locale_domain))
        self.locale = gettext.translation(locale_domain, localedir = locale_folder,
                                          languages = [in_language], fallback = True)

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
                'failed' : self.locale.gettext(
                        'Error encountered on loading Pandas Data Frame '
                        + 'from {file_type} file type (see below)')
                    .replace('{file_type}', operation_details['format'].upper()),
                'success': self.locale.gettext(
                        'All {files_counted} files of type {file_type} '
                        + 'successfully added to a Pandas Data Frame')
                    .replace('{files_counted}', files_counted)
                    .replace('{file_type}', operation_details['format'].upper())
            }
        elif operation_details['operation'] == 'save':
            messages = {
                'failed' : self.locale.gettext(
                        'Error encountered on saving Pandas Data Frame '
                        + 'into a {file_type} file type (see below)')
                    .replace('{file_type}', operation_details['format'].upper()),
                'success': self.locale.gettext(
                        'Pandas Data Frame has just been saved to file "{file_name}", '
                        + 'considering {file_type} as file type')
                    .replace('{file_name}', operation_details['name'])
                    .replace('{file_type}', operation_details['format'].upper()),
            }
        return messages

    def fn_implemented_file_format_validation(self, local_logger, in_file_details):
        given_format_is_implemented = False
        if 'format' in in_file_details:
            given_format_is_implemented = True
            if in_file_details['format'].lower() not in self.implemented_disk_write_file_types:
                given_format_is_implemented = False
                local_logger.error(self.locale.gettext(
                        'File "format" attribute has a value of "{format_value}" '
                        + 'which is not among currently implemented values: '
                        + '"{implemented_file_formats}", '
                        + 'therefore desired file operation is not possible')
                                   .replace('{format_value}', in_file_details['format'].lower())
                                   .replace('{implemented_file_formats}',
                                            '", "'.join(self.implemented_disk_write_file_types)))
        else:
            local_logger.error(self.locale.gettext(
                    'File "format" attribute is mandatory in the file setting, but missing, '
                    + 'therefore desired file operation is not possible'))
        return given_format_is_implemented

    def fn_file_operation_logger(self, local_logger, in_logger_dict):
        messages = self.fn_build_feedback_for_logger(in_logger_dict)
        if in_logger_dict['error details'] is None:
            local_logger.info(messages['success'])
        else:
            local_logger.error(messages['failed'])
            local_logger.error(in_logger_dict['error details'])

    def fn_load_file_into_data_frame(self, in_logger, timer, in_dict):
        timer.start()
        if self.fn_implemented_file_format_validation(in_logger, in_dict):
            in_dict = self.fn_add_missing_defaults_to_dict_message(in_dict)
            in_dict.update({'operation': 'load'})
            in_dict = self.fn_pack_dict_message(in_dict, in_dict['file list'])
            in_dict = self.fn_internal_load_csv_file_into_data_frame(in_dict)
            in_dict = self.fn_internal_load_excel_file_into_data_frame(in_dict)
            in_dict = self.fn_internal_load_json_file_into_data_frame(in_dict)
            in_dict = self.fn_internal_load_parquet_file_into_data_frame(in_dict)
            in_dict = self.fn_internal_load_pickle_file_into_data_frame(in_dict)
            self.fn_file_operation_logger(in_logger, in_dict)
        timer.stop()
        return in_dict['out data frame']

    @staticmethod
    def fn_pack_dict_message(in_dict, in_file_list):
        if in_dict['format'].lower() in ('parquet', 'pickle') \
                and in_dict['compression'].lower() == 'none':
            in_dict['compression'] = None
        return {
            'compression'    : in_dict['compression'],
            'field delimiter': in_dict['field delimiter'],
            'files list'     : in_file_list,
            'files counted'  : len(in_file_list),
            'error details'  : None,
            'format'         : in_dict['format'],
            'name'           : in_dict['name'],
            'in data frame'  : None,
            'operation'      : in_dict['operation'],
            'out data frame' : None,
        }

    def fn_store_data_frame_to_file(self, in_logger, timer, in_data_frame, in_dict):
        timer.start()
        if self.fn_implemented_file_format_validation(in_logger, in_dict):
            in_dict = self.fn_add_missing_defaults_to_dict_message(in_dict)
            in_dict.update({'operation': 'save'})
            in_dict = self.fn_pack_dict_message(in_dict, [])
            in_dict.update({'in data frame': in_data_frame})
            # special case treatment
            in_dict = self.fn_internal_store_data_frame_to_csv_file(in_dict)
            in_dict = self.fn_internal_store_data_frame_to_excel_file(in_dict)
            in_dict = self.fn_internal_store_data_frame_to_json_file(in_dict)
            in_dict = self.fn_internal_store_data_frame_to_parquet_file(in_dict)
            in_dict = self.fn_internal_store_data_frame_to_pickle_file(in_dict)
            self.fn_file_operation_logger(in_logger, in_dict)
        timer.stop()
