"""
Class Converter Specific Needs

Handling specific needs for Extractor script
"""
# useful methods to measure time performance by small pieces of code
from codetiming import Timer
# package to add support for multi-language (i18n)
import gettext
# package to facilitate operating system operations
import os
# package to facilitate common operations
from common.BasicNeeds import BasicNeeds
from common.CommandLineArgumentsManagement import CommandLineArgumentsManagement
from common.DataInputOutput import DataInputOutput
from common.FileOperations import FileOperations
from common.LoggingNeeds import LoggingNeeds


class ProjectNeeds:
    class_bn = None
    class_clam = None
    class_dio = None
    class_fo = None
    config = None
    locale = None
    parameters = None
    script = None
    timer = None

    def __init__(self, destination_script, default_language='en_US'):
        self.script = destination_script
        current_file_basename = os.path.basename(__file__).replace('.py', '')
        lang_folder = os.path.join(os.path.dirname(__file__), current_file_basename + '_Locale')
        self.locale = gettext.translation(current_file_basename, lang_folder,
                                          languages=[default_language])
        # instantiate Basic Needs class
        self.class_bn = BasicNeeds(default_language)
        # instantiate File Operations class
        self.class_fo = FileOperations(default_language)
        # instantiate Command Line Arguments class
        self.class_clam = CommandLineArgumentsManagement(default_language)
        # instantiate Data Manipulator class, useful to manipulate data frames
        self.class_dio = DataInputOutput(default_language)
        # instantiate Logger class
        self.class_ln = LoggingNeeds()

    def fn_check_inputs_specific(self, input_parameters):
        if self.script == 'converter':
            self.class_bn.fn_validate_single_value(
                    os.path.dirname(input_parameters.output_file), 'folder')
        if self.script == 'publisher':
            self.class_bn.fn_validate_single_value(
                    input_parameters.input_file, 'file')
            self.class_bn.fn_validate_single_value(
                    input_parameters.input_credentials_file, 'file')
            self.class_bn.fn_validate_single_value(
                    input_parameters.tableau_server, 'url')

    def initiate_logger_and_timer(self):
        # initiate logger
        self.class_ln.initiate_logger(self.parameters.output_log_file, self.script)
        # initiate localization specific for this script
        # define global timer to use
        self.timer = Timer(self.script,
                           text=self.locale.gettext('Time spent is {seconds}'),
                           logger=self.class_ln.logger.debug)

    def load_configuration(self):
        # load application configuration (inputs are defined into a json file)
        ref_folder = os.path.dirname(__file__).replace('tableau_hyper_management', 'config')
        config_file = os.path.join(ref_folder, 'tableau-hyper-management.json').replace('\\', '/')
        self.config = self.class_fo.fn_open_file_and_get_content(config_file)
        # get command line parameter values
        self.parameters = self.class_clam.parse_arguments(self.config['input_options'][self.script])
        # checking inputs, if anything is invalid an exit(1) will take place
        self.class_bn.fn_check_inputs(self.parameters)
        # checking inputs, if anything is invalid an exit(1) will take place
        self.fn_check_inputs_specific(self.parameters)

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
                .replace('%s', value_to_consider)
            # we finally write the feedback to logger
            in_logger.info(feedback)
        in_logger.info('~' * 50)
        timer.stop()
