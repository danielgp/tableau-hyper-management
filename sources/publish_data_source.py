"""
main - entry point of the package

This file is connecting to a Tableau Server and publishes a local HYPER file
measuring time elapsed (performance)
"""
# package to facilitate operating system locale detection
import locale
# package to handle files/folders and related metadata/operations
import os
# package to facilitate multiple operation system operations
import platform
# Custom classes specific to this package
from tableau_hyper_management.ProjectNeeds import ProjectNeeds
from tableau_hyper_management.TableauServerCommunicator import TableauServerCommunicator
# get current script name
#SCRIPT_NAME = os.path.basename(__file__).replace('.py', '')
SCRIPT_NAME = 'publisher'

# main execution logic
if __name__ == '__main__':
    python_binary = 'python'
    if platform.system() == 'Windows':
        python_binary += '.exe'
    os.system(python_binary + ' ' + os.path.join(os.path.normpath(os.path.dirname(__file__)),
                                                 'localizations_compile.py'))
    locale_implemented = [
        'en_US',
        'it_IT',
        'ro_RO',
    ]
    try:
        region_language = locale.getdefaultlocale('LC_ALL')
        if region_language[0] not in locale_implemented:
            language_to_use = locale_implemented[0]
        else:
            language_to_use = region_language[0]
    except ValueError as err:
        language_to_use = locale_implemented[0]
    # instantiate Extractor Specific Needs class
    class_pn = ProjectNeeds(SCRIPT_NAME, language_to_use)
    # load application configuration (inputs are defined into a json file)
    class_pn.load_configuration()
    # initiate Logging sequence
    class_pn.initiate_logger_and_timer()
    # reflect title and input parameters given values in the log
    class_pn.class_clam.listing_parameter_values(
        class_pn.class_ln.logger, class_pn.timer, 'Tableau Data Source Publisher',
        class_pn.config['input_options'][SCRIPT_NAME], class_pn.parameters)
    relevant_files_list = class_pn.class_fo.fn_build_file_list(
            class_pn.class_ln.logger, class_pn.timer, class_pn.parameters.input_file)
    # log file statistic details
    class_pn.class_fo.fn_store_file_statistics(
            class_pn.class_ln.logger, class_pn.timer, relevant_files_list, 'Input')
    # get the secrets from provided file
    credentials = class_pn.class_fo.fn_open_file_and_get_content(
            class_pn.parameters.input_credentials_file, 'json')
    credentials_dict = credentials['Credentials']['LDAP']['Production']['Default']
    # instantiate main library that ensure Tableau Server communication
    c_tsc = TableauServerCommunicator()
    # initiate Tableau Server connection
    c_tsc.connect_to_tableau_server(class_pn.class_ln.logger, class_pn.timer, {
        'Tableau Server': class_pn.parameters.tableau_server,
        'Tableau Site': class_pn.parameters.tableau_site,
        'Username': credentials_dict['Username'],
        'Password': credentials_dict['Password'],
    })
    # identify relevant project(s) based on given name
    list_project_details = c_tsc.load_tableau_project_ids(
            class_pn.class_ln.logger, class_pn.timer,
            [class_pn.parameters.tableau_project], 'JustOnesMentioned')
    # check if a single project has been identified and if so proceed with publishing
    if c_tsc.is_publishing_possible(
            class_pn.class_ln.logger, class_pn.parameters.tableau_project, list_project_details):
        # perform the publishing of data source
        c_tsc.publish_data_source_to_tableau_server(class_pn.class_ln.logger, class_pn.timer, {
            'Project ID': list_project_details[0],
            'Tableau Extract File': class_pn.parameters.input_file,
            'Publishing Mode': class_pn.parameters.publishing_mode,
        })
    # disconnect from Tableau Server
    c_tsc.disconnect_from_tableau_server(class_pn.class_ln.logger, class_pn.timer)
    # just final message
    class_pn.class_bn.fn_final_message(
            class_pn.class_ln.logger, class_pn.parameters.output_log_file,
            class_pn.timer.timers.total(SCRIPT_NAME))
