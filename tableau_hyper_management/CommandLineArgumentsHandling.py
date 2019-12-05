"""
CommandLineArgumentsHandling - a command line arguments handling library

This library allows handling pre-configured arguments to be received from command line and use them
to call the main package functions

Potential changes to implement:
    argparse = Alternative command line option and argument parsing library.
    https://www.programcreek.com/python/example/748/argparse.ArgumentParser
"""
# standard Python packages
import getopt
import json
import os.path
import sys
# additional Python packages available from PyPi
import pandas as pd
# Custom class specific to this package
from BasicNeeds import BasicNeeds as ClassBN
from TableauHyperApiExtraLogic import TableauHyperApiExtraLogic as ClassTHAEL


class CommandLineArgumentsHandling:
    cfg_dtls = {}

    def fn_assess_option(self, current_option, str_meaning, given_default_value):
        if self.cfg_dtls['options'][current_option]['default_value'] == given_default_value:
            str_feedback_parts = {
                'prefix': 'Fatal Error',
                'verdict': 'Expected -' + current_option + '|--'
                           + self.cfg_dtls['options'][current_option]['option_long']
                           + ' <'
                           + self.cfg_dtls['options'][current_option]['option_sample_value']
                           + '> but nothing of that sort has been seen...',
                'suffix': ':-('
            }
            ln = len(str_feedback_parts['verdict']) - len(str_feedback_parts['prefix'])
            ClassBN.fn_timestamped_print(ClassBN, str_feedback_parts['prefix'] + '_'*ln)
            print(str_feedback_parts['verdict'] + ' ' + str_feedback_parts['suffix'])
            sys.exit(2)
        ClassBN.fn_timestamped_print(ClassBN, str_meaning + ' is "' + given_default_value + '"')

    def fn_build_combined_options(self):
        str_combined_opts = ''
        for option_index, crt_opt in enumerate(self.cfg_dtls['options']):
            if crt_opt is not None:
                str_option_crt = '-' + crt_opt + '|--'\
                                 + self.cfg_dtls['options'][crt_opt]['option_long']
                if 'option_sample_value' in self.cfg_dtls['options'][crt_opt]:
                    str_option_crt += ' <'\
                                      + self.cfg_dtls['options'][crt_opt]['option_sample_value']\
                                      + '>'
                if self.cfg_dtls['options'][crt_opt]['option_type'] == 'optional':
                    str_combined_opts += ' [' + str_option_crt\
                                         + '|if omitted, default value will be considered: '\
                                         + str(self.cfg_dtls['options'][crt_opt]['default_value'])\
                                         + ']'
                else:
                    str_combined_opts += ' ' + str_option_crt
        return str_combined_opts

    def fn_build_long_options(self):
        str_opts = []
        for option_index, crt_lng_opt in enumerate(self.cfg_dtls['options']):
            if crt_lng_opt is not None:
                str_opts.append(option_index)
                str_opts[option_index] = self.cfg_dtls['options'][crt_lng_opt]['option_long'] + '='
        return str_opts

    def fn_build_short_options(self):
        str_short_options = 'h'
        for crt_short_opt in self.cfg_dtls['options']:
            if crt_short_opt is not None:
                if self.cfg_dtls['options'][crt_short_opt]['option_type'] == 'mandatory':
                    str_short_options += crt_short_opt + ':'
                else:
                    str_short_options += crt_short_opt
        return str_short_options

    def fn_command_line_argument_digest(self, help_feedback):
        try:
            opts, args = getopt.getopt(sys.argv[1:],
                                       self.fn_build_short_options(self),
                                       self.fn_build_long_options(self)
                                       )
            return opts
        except getopt.GetoptError:
            print(help_feedback)
            sys.exit(2)

    def fn_command_line_argument_interpretation(self):
        print('#' * 120)
        input_file = ''
        csv_field_separator = ','
        output_file = ''
        verbose = False
        self.fn_load_configuration(self)
        help_feedback = __file__ + self.fn_build_combined_options(self)
        opts = self.fn_command_line_argument_digest(self, help_feedback)
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
        self.fn_assess_option(self, 'i', 'Input file', input_file)
        ClassBN.fn_timestamped_print(ClassBN, 'CSV field separator is "'
                                     + csv_field_separator + '"')
        self.fn_assess_option(self, 'o', 'Output file', output_file)
        print('#' * 120)
        csv_content_df = pd.read_csv(filepath_or_buffer=input_file,
                                     delimiter=csv_field_separator,
                                     cache_dates=True,
                                     index_col=None,
                                     memory_map=True,
                                     encoding='utf-8')
        ClassTHAEL.fn_run_hyper_creation(ClassTHAEL,
                                         csv_content_df,
                                         self.cfg_dtls['data_types'],
                                         output_file, verbose)

    def fn_load_configuration(self):
        with open(os.path.dirname(__file__) + "/config.json", 'r') as json_file:
            self.cfg_dtls = json.load(json_file)
