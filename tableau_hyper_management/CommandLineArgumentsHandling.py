import json
import os.path
import sys
# argparse = Alternative command line option and argument parsing library.

class CommandLineArgumentsHandling:
    config_details = []

    def fn_assess_option(self, current_option, established_default_value):
        if self.config_details['options'][current_option]['default_value'] == established_default_value:
            str_feedback_parts = {
                'prefix': 'Fatal Error',
                'verdict': 'Expected -' + current_option + '|--'
                           + self.config_details['options'][current_option]['option_long']
                           + ' <' + self.config_details['options'][current_option]['option_sample_value']
                           + '> but nothing of that sort has been seen...',
                'suffix': ':-('
            }
            print(str_feedback_parts['prefix']
                  + '_'*(len(str_feedback_parts['verdict']) - len(str_feedback_parts['prefix'])))
            print(str_feedback_parts['verdict'] + ' ' + str_feedback_parts['suffix'])
            sys.exit(2)
        print('Input file is "' + established_default_value + '"')


    def fn_build_combined_options(self):
        str_combined_options = ''
        for option_index, current_option in enumerate(self.config_details['options']):
            if current_option is not None:
                str_option_crt = '-' + current_option + '|--' \
                                 + self.config_details['options'][current_option]['option_long']
                if 'option_sample_value' in self.config_details['options'][current_option]:
                    str_option_crt += ' <' \
                                       + self.config_details['options'][current_option]['option_sample_value'] + '>'
                if self.config_details['options'][current_option]['option_type'] == 'optional':
                    str_combined_options += ' [' + str_option_crt + '|if omitted default value will be considered: ' \
                                            + str(self.config_details['options'][current_option]['default_value']) \
                                            + ']'
                else:
                    str_combined_options += ' ' + str_option_crt
        return str_combined_options


    def fn_build_long_options(self):
        str_long_options = []
        for option_index, current_long_option in enumerate(self.config_details['options']):
            if current_long_option is not None:
                str_long_options.append(option_index)
                str_long_options[option_index] = self.config_details['options'][current_long_option]['option_long'] \
                                                 + '='
        return str_long_options


    def fn_build_short_options(self):
        str_short_options = 'h'
        for current_short_option in self.config_details['options']:
            if current_short_option is not None:
                if self.config_details['options'][current_short_option]['option_type'] == 'mandatory':
                    str_short_options += current_short_option + ':'
                else:
                    str_short_options += current_short_option
        return str_short_options


    def fn_load_configuration(self):
        with open(os.path.dirname(__file__) + "/config.json", 'r') as json_file:
            self.config_details = json.load(json_file)
