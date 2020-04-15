"""
BasicNeeds - useful functions library

This library has functions useful to keep main logic short and simple
"""
# package to handle date and times
from datetime import date, datetime, timedelta
# package to use for checksum calculations (in this file)
import hashlib
# package to handle json files
import json
# package to handle files/folders and related metadata/operations
import os
# package regular expressions
import re


class BasicNeeds:
    cfg_dtls = {}

    def fn_check_inputs(self, input_parameters, input_script):
        if input_parameters.output_log_file is not None:
            # checking log folder first as there's all further messages will be stored
            self.fn_validate_single_value(os.path.dirname(input_parameters.output_log_file),
                                          'folder', 'log file')

    def fn_final_message(self, local_logger, log_file_name, performance_in_seconds):
        total_time_string = str(timedelta(seconds=performance_in_seconds))
        if log_file_name == 'None':
            self.fn_timestamped_print('Application finished, whole script took '
                                      + total_time_string)
        else:
            local_logger.info(f'Total execution time was ' + total_time_string)
            self.fn_timestamped_print('Application finished, '
                                      + 'for complete logged details please check '
                                      + log_file_name)

    def fn_get_file_content(self, in_file_handler, in_content_type):
        if in_content_type == 'json':
            try:
                json_interpreted_details = json.load(in_file_handler)
                self.fn_timestamped_print('I have interpreted JSON structure from given file')
                return json_interpreted_details
            except Exception as e:
                self.fn_timestamped_print('Error encountered when trying to interpret JSON')
                print(e)
        elif in_content_type == 'raw':
            raw_interpreted_file = in_file_handler.read()
            self.fn_timestamped_print('I have read file entire content')
            return raw_interpreted_file
        else:
            self.fn_timestamped_print('Unknown content type provided, '
                                      + 'expected either "json" or "raw" but got '
                                      + in_content_type)

    @staticmethod
    def fn_get_file_statistics(file_to_evaluate):
        try:
            file_sha512 = hashlib.sha512(open(file=file_to_evaluate, mode='r', encoding='utf-8')\
                                         .read().encode()).hexdigest()
        except UnicodeDecodeError:
            file_sha512 = hashlib.sha512(open(file=file_to_evaluate, mode='r', encoding='mbcs')\
                                         .read().encode()).hexdigest()
        file_dates = {
            'created': os.path.getctime(file_to_evaluate),
            'modified': os.path.getctime(file_to_evaluate),
        }
        file_info = {
            'date when created': date.strftime(datetime.fromtimestamp(file_dates['created']),
                                               '%Y-%m-%d %H:%M:%S.%f'),
            'date when last modified': date.strftime(datetime.fromtimestamp(file_dates['modified']),
                                                     '%Y-%m-%d %H:%M:%S.%f'),
            'size [bytes]': os.path.getsize(file_to_evaluate),
            'SHA512-Checksum': file_sha512,
        }
        return file_info

    def fn_load_configuration(self):
        relevant_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.cfg_dtls = self.fn_open_file_and_get_content(relevant_file)

    @staticmethod
    def fn_multi_line_string_to_single_line(input_string):
        string_to_return = input_string.replace('\n', ' ').replace('\r', ' ')
        return re.sub(r'\s{2,100}', ' ', string_to_return).replace(' , ', ', ').strip()

    @staticmethod
    def fn_numbers_with_leading_zero(input_number_as_string, digits):
        final_number = input_number_as_string
        if len(input_number_as_string) < digits:
            final_number = '0' * (digits - len(input_number_as_string)) + input_number_as_string
        return final_number

    def fn_open_file_and_get_content(self, input_file, content_type='json'):
        if os.path.isfile(input_file):
            with open(input_file, 'r') as file_handler:
                self.fn_timestamped_print('I have opened file: ' + input_file)
                return self.fn_get_file_content(file_handler, content_type)
        else:
            self.fn_timestamped_print('Given file ' + input_file
                                      + ' does not exist, please check your inputs!')

    def fn_optional_print(self, boolean_variable, string_to_print):
        if boolean_variable:
            self.fn_timestamped_print(string_to_print)

    def fn_store_file_statistics(self, local_logger, timmer, file_name, file_meaning):
        timmer.start()
        file_name_variable_type = str(type(file_name))
        list_file_names = [file_name]
        if file_name_variable_type == "<class 'list'>":
            list_file_names = file_name
        for current_file_name in list_file_names:
            local_logger.info(file_meaning + ' file "' + current_file_name
                              + '" has the following characteristics: '
                              + str(self.fn_get_file_statistics(current_file_name)))
        timmer.stop()

    @staticmethod
    def fn_timestamped_print(string_to_print):
        print(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f %Z")
              + ' - ' + string_to_print)

    @staticmethod
    def fn_validate_one_value(value_to_validate, validation_type, name_meaning):
        is_fatal_error = False
        message = ''
        if validation_type == 'file':
            is_fatal_error = (not os.path.isfile(value_to_validate))
            message = 'Given ' + name_meaning + ' "' + value_to_validate \
                      + '" does not exist, please check your inputs!'
        elif validation_type == 'folder':
            is_fatal_error = (not os.path.isdir(value_to_validate))
            message = 'Given ' + name_meaning + ' "' + value_to_validate \
                      + '" does not exist, please check your inputs!'
        elif validation_type == 'url':
            url_reg_expression = 'https?://(?:www)?(?:[\\w-]{2,255}(?:\\.\\w{2,66}){1,2})'
            is_fatal_error = (not re.match(url_reg_expression, value_to_validate))
            message = 'Given ' + name_meaning + ' "' + value_to_validate \
                      + '" does not seem a valid one, please check your inputs!'
        return {
            'is_fatal_error': is_fatal_error,
            'message': message,
        }

    def fn_validate_single_value(self, value_to_validate, validation_type, name_meaning):
        validation_details = self.fn_validate_one_value(value_to_validate, validation_type,
                                                        name_meaning)
        if validation_details['is_fatal_error']:
            self.fn_timestamped_print(validation_details['message'])
            exit(1)
