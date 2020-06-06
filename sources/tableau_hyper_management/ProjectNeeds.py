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
from .BasicNeeds import BasicNeeds
from .CommandLineArgumentsManagement import CommandLineArgumentsManagement
from .DataInputOutput import DataInputOutput
from .FileOperations import FileOperations
from .ParameterHandling import ParameterHandling
from .LoggingNeeds import LoggingNeeds


class ProjectNeeds:
    class_bn = None
    class_clam = None
    class_dio = None
    class_fo = None
    class_ph = None
    config = None
    locale = None
    parameters = None
    script = None
    timer = None

    def __init__(self, in_dict, script_title):
        self.script = in_dict['script name']
        self.initiate_locale(in_dict['language'])
        self.initiate_classes(in_dict['language'])
        # load application configuration (inputs are defined into a json file)
        self.load_configuration()
        # adding a special case data type
        self.config['data_types']['empty'] = '^$'
        self.config['data_types']['str'] = ''
        # initiate Logging sequence
        self.initiate_logger_and_timer()
        # reflect title and input parameters given values in the log
        self.class_clam.listing_parameter_values(
            self.class_ln.logger, self.timer, in_dict['title'],
            self.config['input_options'][self.script], self.parameters)

    def fn_check_inputs_specific(self, input_parameters):
        if self.script == 'publisher':
            self.class_bn.fn_timestamped_print(self.locale.gettext(
                'Checking if provided input credentials file exists'))
            self.class_bn.fn_validate_single_value(input_parameters.input_credentials_file, 'file')
            self.class_bn.fn_timestamped_print(self.locale.gettext(
                'Checking if provided Tableau Server url is valid'))
            self.class_bn.fn_validate_single_value(input_parameters.tableau_server, 'url')

    def initiate_classes(self, default_language):
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
        # instantiate Parameter Handling class
        self.class_ph = ParameterHandling(default_language)

    def initiate_locale(self, default_language):
        file_parts = os.path.normpath(os.path.abspath(__file__)).replace('\\', os.path.altsep)\
            .split(os.path.altsep)
        locale_domain = file_parts[(len(file_parts)-1)].replace('.py', '')
        locale_folder = os.path.normpath(os.path.join(
            os.path.join(os.path.altsep.join(file_parts[:-2]), 'project_locale'), locale_domain))
        self.locale = gettext.translation(
            locale_domain, localedir=locale_folder, languages=[default_language], fallback=True)

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

    def source_vs_destination_file_modification_assesment(self, in_logger, timer, in_dict):
        """
        Checks if any source file is newer than destination

        :param in_logger: logger handler to capture running details
        :param timer: pointer to measure code performance
        :param in_dict: dictionary containing following keys with relevant values:
            "destination file" and "list source files"
        :return: either None or localized term for "newer"
        """
        timer.start()
        destination_file_times = self.class_fo.fn_get_file_dates_raw(in_dict['destination file'])
        source_files_count = len(in_dict['list source files'])
        loop_counter = 0
        stop_verdict = self.class_fo.locale.gettext('newer')
        verdict = None
        while verdict != stop_verdict and loop_counter < source_files_count:
            crt_file = in_dict['list source files'][loop_counter]
            crt_verdict = self.class_fo.fn_get_file_datetime_verdict(
                in_logger, crt_file, 'last modified', destination_file_times['last modified'])
            if crt_verdict == stop_verdict:
                verdict = crt_verdict
            loop_counter += 1
        timer.stop()
        return verdict
