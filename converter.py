"""
main - entry point of the package

This file is performing CSV read into HYPER file and measures time elapsed (performance)
"""
# standard Python packages
import os.path
# additional packages to be installed from PyPi
import pandas as pd
# Custom classes specific to this package
from tableau_hyper_management.BasicNeeds import BasicNeeds
from tableau_hyper_management.CommandLineArgumentsManagement import CommandLineArgumentsManagement
from tableau_hyper_management.LoggingNeeds import LoggingNeeds
from tableau_hyper_management.TableauHyperApiExtraLogic import TableauHyperApiExtraLogic
from tableau_hyper_management.TypeDetermination import TypeDetermination
# package to measure portions of code performance
from codetiming import Timer
# get current script name
current_script_name = os.path.basename(__file__).replace('.py', '')

# main execution logic
if __name__ == '__main__':
    c_bn = BasicNeeds()
    c_bn.fn_load_configuration()
    # instate Class named Command Line Arguments
    c_clam = CommandLineArgumentsManagement()
    parameters_in = c_clam.parse_arguments(c_bn.cfg_dtls['input_options']['converter'])
    # checking inputs, if anything is invalid an exit(1) will take place
    c_bn.fn_check_inputs(parameters_in, current_script_name)
    # initiate logger
    c_ln = LoggingNeeds()
    c_ln.initiate_logger(parameters_in.output_log_file, 'thm_converter')
    # define global timer to use
    t = Timer('thm',
              text      = 'Time spent is {seconds} ',
              logger    = c_ln.logger.debug
              )
    t.start()
    # marking start of the Log
    c_ln.logger.info('='*50)
    c_ln.logger.info('Tableau Hyper Management started')
    # reflect input parameters given values
    c_clam.listing_parameter_values(c_ln.logger, c_bn.cfg_dtls['input_options']['converter'], parameters_in)
    t.stop()
    # intake given CSV file into a Pandas Data Frame
    t.start()
    csv_content_df = pd.read_csv(filepath_or_buffer = parameters_in.input_file,
                                 delimiter          = parameters_in.csv_field_separator,
                                 cache_dates        = True,
                                 index_col          = None,
                                 memory_map         = True,
                                 low_memory         = False,
                                 encoding           = 'utf-8',
                                 )
    c_ln.logger.info('Given CSV file ' + parameters_in.input_file
                     + ' has been loaded into a Pandas Data Frame successfully')
    t.stop()
    t.start()
    # advanced detection of data type within Data Frame
    c_td = TypeDetermination()
    detected_csv_structure = c_td.fn_detect_csv_structure(c_ln.logger, csv_content_df, parameters_in,
                                                          c_bn.cfg_dtls['data_types'])
    t.stop()
    t.start()
    # create HYPER from Data Frame
    c_thael = TableauHyperApiExtraLogic()
    c_thael.fn_run_hyper_creation(c_ln.logger, csv_content_df, detected_csv_structure, parameters_in)
    t.stop()
    c_bn.fn_final_message(c_ln.logger, parameters_in.output_log_file, t.timers.total('thm_converter'))
