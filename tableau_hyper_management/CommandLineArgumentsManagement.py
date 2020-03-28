'''
CommandLineArgumentManagement - library to manage input parameters from command line

This library allows handling pre-configured arguments to be received from command line and use them
to call the main package functions
'''

import argparse


class CommandLineArgumentsManagement:

    @staticmethod
    def listing_parameter_values(self, local_logger, given_parameter_values):
        local_logger.info('~' * 50)
        local_logger.info('Overview of input parameter given values')
        local_logger.info('~' * 50)
        local_logger.info('Input file is ' + given_parameter_values.input_file)
        local_logger.info('CSV field separator is ' + given_parameter_values.csv_field_separator)
        local_logger.info('Unique values to analyze is limited to '
                          + str(given_parameter_values.unique_values_to_analyze_limit))
        local_logger.info('Output file is ' + given_parameter_values.output_file)
        local_logger.info('~' * 50)

    def parse_arguments(self, configuration_details):
        parser = argparse.ArgumentParser()
        for input_key, attributes in configuration_details.items():
            action_value = self.translate_default_to_action(attributes['default_value'])
            if action_value is None:
                parser.add_argument('-' + input_key, '--' + attributes['option_long'],
                                    required=attributes['option_required'],
                                    default=attributes['default_value'],
                                    help=attributes['option_sample_value'])
            else:
                parser.add_argument('-' + input_key, '--' + attributes['option_long'],
                                    required=attributes['option_required'],
                                    default=attributes['default_value'],
                                    action=action_value)
        parser.add_argument('-v', '--verbose', required=False, default=False, action='store_true')
        return parser.parse_args()

    @staticmethod
    def translate_default_to_action(given_default_value):
        if given_default_value == True:
            return 'store_true'
        elif given_default_value == False:
            return 'store_false'
        else:
            return None
