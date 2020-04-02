"""
BasicNeeds - useful functions library

This library has functions useful to keep main logic short and simple
"""

# standard Python packages
from datetime import datetime, timedelta
import json
import os.path
import re


class BasicNeeds:
    cfg_dtls = {}

    def fn_check_inputs(self, input_parameters, input_script):
        # checking log folder first as there's all further messages will be stored
        self.fn_validate_single_value(os.path.dirname(input_parameters.output_log_file), 'folder', 'log file')
        # checking input file as the main point of whole logic revolves around it
        self.fn_validate_single_value(input_parameters.input_file, 'file', 'input file')
        # checking script specific inputs
        if input_script == 'converter':
            self.fn_validate_single_value(os.path.dirname(input_parameters.output_file), 'folder', 'output file')
        elif input_script == 'publish_data_source':
            self.fn_validate_single_value(input_parameters.input_credentials_file, 'file', 'credentials file')
            self.fn_validate_single_value(input_parameters.tableau_server, 'url', 'Tableau Server URL')

    def fn_final_message(self, local_logger, log_file_name, performance_in_seconds):
        total_time_string = str(timedelta(seconds=performance_in_seconds))
        if log_file_name == 'None':
            self.fn_timestamped_print('Application finished, whole script took ' + total_time_string)
        else:
            local_logger.info(f'Total execution time was ' + total_time_string)
            self.fn_timestamped_print('Application finished, for complete logged details please check ' + log_file_name)

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

    def fn_load_configuration(self):
        relevant_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.cfg_dtls = self.fn_open_file_and_get_its_content(relevant_file)
        # adding a special case data type
        self.cfg_dtls['data_types']['str'] = ''

    def fn_open_file_and_get_its_content(self, input_file, content_type='json'):
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

    @staticmethod
    def fn_timestamped_print(string_to_print):
        print(datetime.utcnow().strftime("%Y-%b-%d %H:%M:%S.%f %Z")
              + ' - ' + string_to_print)

    def fn_validate_single_value(self, value_to_validate, validation_type, name_meaning):
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
            is_fatal_error = (not re.match('https?://(?:www)?(?:[\w-]{2,255}(?:\.\w{2,66}){1,2})', value_to_validate))
            message = 'Given ' + name_meaning + ' "' + value_to_validate \
                      + '" does not seem a valid one, please check your inputs!'
        if is_fatal_error:
            self.fn_timestamped_print(message)
            exit(1)
