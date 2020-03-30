'''
CommandLineArgumentManagement - library to manage input parameters from command line

This library allows handling pre-configured arguments to be received from command line and use them
to call the main package functions
'''

import argparse


class CommandLineArgumentsManagement:

    @staticmethod
    def listing_parameter_values(self, local_logger, configuration_details, given_parameter_values):
        local_logger.info('~' * 50)
        local_logger.info('Overview of input parameter given values')
        local_logger.info('~' * 50)
        parameter_values_dictionary = given_parameter_values.__dict__
        for input_key, attributes in configuration_details.items():
            # checking first if short key was provided, otherwise consider longer
            if input_key in parameter_values_dictionary:
                key_value_to_consider = input_key
            else:
                key_value_to_consider = attributes['option_long'].replace('-', '_')
            # having the key consider we determine the value of the current parameter
            value_to_consider = parameter_values_dictionary[key_value_to_consider]
            # we build the parameter feedback considering "option_description"
            # and replacing %s with parameter value
            feedback = attributes['option_description'] % value_to_consider
            # we finally write the feedback to logger
            local_logger.info(feedback)
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
