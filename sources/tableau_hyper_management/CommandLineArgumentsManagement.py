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
        file_parts = os.path.normpath(os.path.abspath(__file__)).replace('\\', os.path.altsep)\
            .split(os.path.altsep)
        locale_domain = file_parts[(len(file_parts)-1)].replace('.py', '')
        locale_folder = os.path.normpath(os.path.join(
            os.path.join(os.path.altsep.join(file_parts[:-2]), 'project_locale'), locale_domain))
        self.locale = gettext.translation(locale_domain, localedir=locale_folder,
                                          languages=[in_language], fallback=True)

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
