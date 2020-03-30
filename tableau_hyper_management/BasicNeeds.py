"""
BasicNeeds - useful functions library

This library has functions useful to keep main logic short and simple
"""

# standard Python packages
from datetime import datetime, timezone, timedelta
import json
import os.path


class BasicNeeds:
    cfg_dtls = {}

    def fn_final_message(self, local_logger, timmer, log_file_name):
        total_time_string = str(timedelta(seconds = timmer.timers.total('thm')))
        if log_file_name == 'None':
            self.fn_timestamped_print(self, 'Application finished, whole script took '
                                      + total_time_string)
        else:
            local_logger.info(f'Total execution time was ' + total_time_string)
            self.fn_timestamped_print(self, 'Application finished, '
                                      + 'for complete logged details please check ' + log_file_name)

    def fn_get_file_content(self, in_file_handler, in_content_type):
        if in_content_type == 'json':
            try:
                json_interpreted_details = json.load(in_file_handler)
                self.fn_timestamped_print(self, 'I have interpreted JSON structure from given file')
                return json_interpreted_details
            except Exception as e:
                self.fn_timestamped_print(self, 'Error encountered when trying to interpret JSON')
                print(e)
        elif in_content_type == 'raw':
            raw_interpreted_file = in_file_handler.read()
            self.fn_timestamped_print(self, 'I have read file entire content')
            return raw_interpreted_file
        else:
            self.fn_timestamped_print(self, 'Unknown content type provided, '
                                      + 'expected either "json" or "raw" but got '
                                      + in_content_type)

    def fn_load_configuration(self):
        relevant_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.cfg_dtls = self.fn_open_file_and_get_its_content(self, relevant_file)
        # adding a special case data type
        self.cfg_dtls['data_types']['str'] = ''

    def fn_open_file_and_get_its_content(self, input_file, content_type = 'json'):
        if os.path.isfile(input_file):
            with open(input_file, 'r') as file_handler:
                self.fn_timestamped_print(self, 'I have opened file: ' + input_file)
                return self.fn_get_file_content(self, file_handler, content_type)
        else:
            self.fn_timestamped_print(self, 'Given file ' + input_file
                                      + ' does not exist, please check your inputs!')

    def fn_optional_print(self, boolean_variable, string_to_print):
        if boolean_variable:
            self.fn_timestamped_print(self, string_to_print)

    @staticmethod
    def fn_timestamped_print(self, string_to_print):
        print(datetime.utcnow().strftime("%Y-%b-%d %H:%M:%S.%f %Z")
              + ' - ' + string_to_print)
