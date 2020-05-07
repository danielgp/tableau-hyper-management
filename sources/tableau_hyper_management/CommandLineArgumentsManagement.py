"""
CommandLineArgumentManagement - library to manage input parameters from command line

This library allows handling pre-configured arguments to be received from command line and use them
to call the main package functions
"""
# package to handle arguments from command line
import argparse
# package to add support for multi-language (i18n)
import gettext
# package to facilitate operating system operations
import os


class CommandLineArgumentsManagement:
    locale = None

    def __init__(self, in_language='en_US'):
        current_script = os.path.basename(__file__).replace('.py', '')
        lang_folder = os.path.join(os.path.dirname(__file__), current_script + '_Locale')
        self.locale = gettext.translation(current_script, lang_folder, languages=[in_language])

    def listing_parameter_values(self, in_logger, timer, title, in_config, given_parameter_values):
        timer.start()
        in_logger.info('=' * 50)
        in_logger.info(self.locale.gettext('{application_name} has started')
                       .replace('{application_name}', title))
        in_logger.info('~' * 50)
        in_logger.info(self.locale.gettext('Overview of input parameter given values'))
        in_logger.info('~' * 50)
        parameter_values_dictionary = given_parameter_values.__dict__
        for input_key, attributes in in_config.items():
            # checking first if short key was provided, otherwise consider longer
            if input_key in parameter_values_dictionary:
                key_value_to_consider = input_key
            else:
                key_value_to_consider = attributes['option_long'].replace('-', '_')
            # having the key consider we determine the value of the current parameter
            value_to_consider = parameter_values_dictionary[key_value_to_consider]
            # we build the parameter feedback considering "option_description"
            # and replacing %s with parameter value
            feedback = self.locale.gettext(attributes['option_description']) \
                .replace('%s', str(value_to_consider))
            # we finally write the feedback to logger
            in_logger.info(feedback)
        in_logger.info('~' * 50)
        timer.stop()

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
        if given_default_value is True:
            return 'store_true'
        elif given_default_value is False:
            return 'store_false'
        else:
            return None
