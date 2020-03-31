"""
main - entry point of the package

This file is connecting to a Tableau Server and publishes a local HYPER file
measuring time elapsed (performance)
"""

# standard Python packages
import os
import os.path as os_path
from datetime import timedelta
# package to measure portions of code performance
from codetiming import Timer


# Custom classes specific to this package
from tableau_hyper_management.BasicNeeds import BasicNeeds as ClassBN
from tableau_hyper_management.LoggingNeeds import LoggingNeeds as ClassLN
from tableau_hyper_management.CommandLineArgumentsManagement import \
    CommandLineArgumentsManagement as ClassCLAM
from tableau_hyper_management.TableauServerCommunicator import TableauServerCommunicator as ClassTSC

# main execution logic
if __name__ == '__main__':
    ClassBN.fn_load_configuration(ClassBN)
    parameters_in = ClassCLAM.parse_arguments(ClassCLAM,
                                              ClassBN.cfg_dtls['input_options']['publisher'])
    credentials = ClassBN.fn_open_file_and_get_its_content(ClassBN,
                                                           parameters_in.input_credentials_file,
                                                           'json')
    credentials_to_use = credentials['Credentials']['LDAP']['LDAP']['LDAP']['Production']['Default']
    # initiate logger
    ClassLN.initiate_logger(ClassLN, parameters_in.output_log_file, 'thm_publisher')
    # define global timer to use
    t = Timer('thm',
              text      = 'Time spent is {seconds} ',
              logger    = ClassLN.logger.debug
              )
    t.start()
    # marking start of the Log
    ClassLN.logger.info('='*50)
    ClassLN.logger.info('Tableau Hyper Publisher started')
    # reflect input parameters given values
    ClassCLAM.listing_parameter_values(ClassCLAM, ClassLN.logger,
                                       ClassBN.cfg_dtls['input_options']['publisher'],
                                       parameters_in,
                                       )
    t.stop()
    # check if provided Hyper file actually exists
    if os_path.isfile(parameters_in.input_file):
        tableau_connecting_details = {
            'Tableau Server'    : parameters_in.tableau_server,
            'Tableau Site'      : parameters_in.tableau_site,
            'Username'          : credentials_to_use['Username'],
            'Password'          : credentials_to_use['Password'],
        }
        ClassTSC.connect_to_tableau_server(ClassTSC, ClassLN.logger, t, tableau_connecting_details)
        relevant_project = [parameters_in.tableau_project]
        relevant_project_details = ClassTSC.load_tableau_project_ids(ClassTSC, ClassLN.logger, t,
                                                                     relevant_project,
                                                                     'JustOnesMentioned')
        if ClassTSC.is_publishing_possible(ClassTSC, ClassLN.logger,
                                           parameters_in.tableau_project,
                                           relevant_project_details):
            publishing_details = {
                'Project ID'            : relevant_project_details[0],
                'Tableau Extract File'  : parameters_in.input_file,
                'Publishing Mode'       : parameters_in.publishing_mode,
            }
            ClassTSC.publish_data_source_to_tableau_server(ClassTSC, ClassLN.logger, t,
                                                           publishing_details)
        ClassTSC.disconnect_from_tableau_server(ClassTSC, ClassLN.logger, t)
    else:
        # doesn't exist
        ClassLN.logger.error('Given file ' + parameters_in.input_file
                             + ' does not exist, please check your inputs!')
    ClassBN.fn_final_message(ClassBN, ClassLN.logger, t, parameters_in.output_log_file)
