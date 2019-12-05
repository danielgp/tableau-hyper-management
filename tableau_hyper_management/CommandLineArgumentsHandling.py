import getopt
import json
import os.path
import pandas as pd
import sys
# argparse = Alternative command line option and argument parsing library.

from . import TableauHyperApiExtraLogic as ClassTHAEL


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

    def fn_command_line_argument_interpretation(self, argv):
        # https://www.programcreek.com/python/example/748/argparse.ArgumentParser
        print('#' * 120)
        input_file = ''
        csv_field_separator = ','
        output_file = ''
        verbose = False
        self.fn_load_configuration(self)
        help_feedback = __file__ + self.fn_build_combined_options(self)
        try:
            opts, args = getopt.getopt(argv, self.fn_build_short_options(self), self.fn_build_long_options(self))
        except getopt.GetoptError:
            print(help_feedback)
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(help_feedback)
                sys.exit()
            elif opt in ("-i", "--input-file"):
                input_file = arg
            elif opt in ("-s", "--csv-field-separator"):
                csv_field_separator = arg
            elif opt in ("-o", "--output-file"):
                output_file = arg
            elif opt in ("-v", "--verbose"):
                verbose = True
            else:
                assert False, "Unhandled Option: " + arg
        self.fn_assess_option(self, 'i', input_file)
        print('CSV field separator is "' + csv_field_separator + '"')
        self.fn_assess_option(self, 'o', output_file)
        print('#' * 120)
        csv_content_df = pd.read_csv(filepath_or_buffer = input_file,
                                     delimiter = csv_field_separator,
                                     cache_dates = True,
                                     index_col = None,
                                     memory_map = True,
                                     encoding = 'utf-8')
        formats_to_evaluate = self.config_details['data_types']
        ClassTHAEL.fn_run_hyper_creation(ClassTHAEL, csv_content_df, formats_to_evaluate, output_file, verbose)

    def fn_load_configuration(self):
        with open(os.path.dirname(__file__) + "/config.json", 'r') as json_file:
            self.config_details = json.load(json_file)
