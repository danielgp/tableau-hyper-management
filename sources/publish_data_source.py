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
from sources.tableau_hyper_management.BasicNeeds import BasicNeeds
from sources.tableau_hyper_management.LoggingNeeds import LoggingNeeds
from sources.tableau_hyper_management.CommandLineArgumentsManagement \
    import CommandLineArgumentsManagement
from sources.tableau_hyper_management.TableauServerCommunicator import TableauServerCommunicator

# get current script name
current_script_name = os.path.basename(__file__).replace('.py', '')

# main execution logic
if __name__ == '__main__':
    # instantiate Basic Needs class
    c_bn = BasicNeeds()
    # load application configuration (inputs are defined into a json file)
    c_bn.fn_load_configuration()
    # instantiate CommandLine Arguments Management class
    c_clam = CommandLineArgumentsManagement()
    parameters_in = c_clam.parse_arguments(c_bn.cfg_dtls['input_options']['publisher'])
    # checking inputs, if anything is invalid an exit(1) will take place
    c_bn.fn_check_inputs(parameters_in, current_script_name)
    # get the secrets from provided file
    credentials = c_bn.fn_open_file_and_get_content(parameters_in.input_credentials_file, 'json')
    credentials_dict = credentials['Credentials']['LDAP']['LDAP']['LDAP']['Production']['Default']
    # instantiate Logger class
    c_ln = LoggingNeeds()
    # initiate logger
    c_ln.initiate_logger(parameters_in.output_log_file, 'thm_publish_data_source')
    # define global timer to use
    t = Timer('thm_publish_data_source', text='Time spent is {seconds} ', logger=c_ln.logger.debug)
    # reflect input parameters given values
    c_clam.listing_parameter_values(c_ln.logger, t, 'Tableau Hyper Publisher',
                                    c_bn.cfg_dtls['input_options']['publisher'], parameters_in)
    # store statistics about input file
    c_bn.fn_store_file_statistics(c_ln.logger, t, parameters_in.input_file, 'Input')
    # instantiate main library that ensure Tableau Server communication
    c_tsc = TableauServerCommunicator()
    # initiate Tableau Server connection
    c_tsc.connect_to_tableau_server(c_ln.logger, t, {
        'Tableau Server': parameters_in.tableau_server,
        'Tableau Site': parameters_in.tableau_site,
        'Username': credentials_dict['Username'],
        'Password': credentials_dict['Password'],
    })
    # identify relevant project(s) based on given name
    relevant_project_details = c_tsc.load_tableau_project_ids(c_ln.logger, t,
                                                              [parameters_in.tableau_project],
                                                              'JustOnesMentioned')
    # check if a single project has been identified and if so proceed with publishing
    if c_tsc.is_publishing_possible(c_ln.logger, parameters_in.tableau_project,
                                    relevant_project_details):
        # perform the publishing of data source
        c_tsc.publish_data_source_to_tableau_server(c_ln.logger, t, {
            'Project ID': relevant_project_details[0],
            'Tableau Extract File': parameters_in.input_file,
            'Publishing Mode': parameters_in.publishing_mode,
        })
    # disconnect from Tableau Server
    c_tsc.disconnect_from_tableau_server(c_ln.logger, t)
    # just final message
    c_bn.fn_final_message(c_ln.logger, parameters_in.output_log_file,
                          t.timers.total('thm_publish_data_source'))
