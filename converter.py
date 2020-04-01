"""
main - entry point of the package

This file is performing CSV read into HYPER file and measures time elapsed (performance)
"""

# standard Python packages
import os.path as os_path
# additional packages to be installed from PyPi
import pandas as pd
# Custom classes specific to this package
from tableau_hyper_management import CommandLineArgumentsManagement
from tableau_hyper_management import LoggingNeeds
from tableau_hyper_management import TableauHyperApiExtraLogic
from tableau_hyper_management import TypeDetermination
# package to measure portions of code performance
from codetiming import Timer

# main execution logic
if __name__ == '__main__':
    c_td = TypeDetermination()
    c_td.fn_load_configuration()
    # instate Class named Command Line Arguments
    c_clam = CommandLineArgumentsManagement()
    parameters_in = c_clam.parse_arguments(c_td.cfg_dtls['input_options']['converter'])
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
    c_clam.listing_parameter_values(c_ln.logger,
                                    c_td.cfg_dtls['input_options']['converter'],
                                    parameters_in)
    t.stop()
    # initiate Data Frame from specified CSV file
    if os_path.isfile(parameters_in.input_file):
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
        detected_csv_structure = c_td.fn_detect_csv_structure(c_ln.logger,
                                                              csv_content_df, parameters_in)
        t.stop()
        t.start()
        # create HYPER from Data Frame
        c_thael = TableauHyperApiExtraLogic()
        c_thael.fn_run_hyper_creation(c_ln.logger, csv_content_df,
                                      detected_csv_structure, parameters_in)
        t.stop()
    else:
        # doesn't exist
        c_ln.logger.error('Given file ' + parameters_in.input_file
                          + ' does not exist, please check your inputs!')
    c_td.fn_final_message(c_ln.logger, t, parameters_in.output_log_file)
