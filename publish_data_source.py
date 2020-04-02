"""
main - entry point of the package

This file is connecting to a Tableau Server and publishes a local HYPER file
measuring time elapsed (performance)
"""
# standard Python packages
import os.path
# package to measure portions of code performance
from codetiming import Timer
# Custom classes specific to this package
from tableau_hyper_management.BasicNeeds import BasicNeeds
from tableau_hyper_management.LoggingNeeds import LoggingNeeds
from tableau_hyper_management.CommandLineArgumentsManagement import CommandLineArgumentsManagement
from tableau_hyper_management.TableauServerCommunicator import TableauServerCommunicator
# get current script name
current_script_name = os.path.basename(__file__).replace('.py', '')

# main execution logic
if __name__ == '__main__':
    c_bn = BasicNeeds()
    c_bn.fn_load_configuration()
    c_clam = CommandLineArgumentsManagement()
    parameters_in = c_clam.parse_arguments(c_bn.cfg_dtls['input_options']['publisher'])
    # checking inputs, if anything is invalid an exit(1) will take place
    c_bn.fn_check_inputs(parameters_in, current_script_name)
    # get the secrets from provided file
    credentials = c_bn.fn_open_file_and_get_its_content(parameters_in.input_credentials_file, 'json')
    credentials_to_use = credentials['Credentials']['LDAP']['LDAP']['LDAP']['Production']['Default']
    # initiate logger
    c_ln = LoggingNeeds()
    c_ln.initiate_logger(parameters_in.output_log_file, 'thm_publish_data_source')
    # define global timer to use
    t = Timer('thm',
              text      = 'Time spent is {seconds} ',
              logger    = c_ln.logger.debug
              )
    t.start()
    # marking start of the Log
    c_ln.logger.info('='*50)
    c_ln.logger.info('Tableau Hyper Publisher started')
    # reflect input parameters given values
    c_clam.listing_parameter_values(c_ln.logger, c_bn.cfg_dtls['input_options']['publisher'], parameters_in)
    t.stop()
    tableau_connecting_details = {
        'Tableau Server'    : parameters_in.tableau_server,
        'Tableau Site'      : parameters_in.tableau_site,
        'Username'          : credentials_to_use['Username'],
        'Password'          : credentials_to_use['Password'],
    }
    c_tsc = TableauServerCommunicator()
    c_tsc.connect_to_tableau_server(c_ln.logger, t, tableau_connecting_details)
    relevant_project = [parameters_in.tableau_project]
    relevant_project_details = c_tsc.load_tableau_project_ids(c_ln.logger, t, relevant_project, 'JustOnesMentioned')
    if c_tsc.is_publishing_possible(c_ln.logger, parameters_in.tableau_project, relevant_project_details):
        publishing_details = {
            'Project ID'            : relevant_project_details[0],
            'Tableau Extract File'  : parameters_in.input_file,
            'Publishing Mode'       : parameters_in.publishing_mode,
        }
        c_tsc.publish_data_source_to_tableau_server(c_ln.logger, t, publishing_details)
    c_tsc.disconnect_from_tableau_server(c_ln.logger, t)
    c_bn.fn_final_message(c_ln.logger, parameters_in.output_log_file, t.timers.total('thm_publish_data_source'))
