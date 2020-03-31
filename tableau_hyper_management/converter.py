"""
main - entry point of the package

This file is performing CSV read into HYPER file and measures time elapsed (performance)
"""

# standard Python packages
import os.path as os_path
from datetime import timedelta
# package to measure portions of code performance
from codetiming import Timer

# additional packages to be installed from PyPi
import pandas as pd

# Custom classes specific to this package
from tableau_hyper_management.LoggingNeeds import LoggingNeeds as ClassLN
from tableau_hyper_management.TypeDetermination import ClassBN
from tableau_hyper_management.TypeDetermination import TypeDetermination as ClassTD
from tableau_hyper_management.CommandLineArgumentsManagement import \
    CommandLineArgumentsManagement as ClassCLAM
from tableau_hyper_management.TableauHyperApiExtraLogic import \
    TableauHyperApiExtraLogic as ClassTHAEL

# main execution logic
if __name__ == '__main__':
    ClassBN.fn_load_configuration(ClassBN)
    parameters_in = ClassCLAM.parse_arguments(ClassCLAM,
                                              ClassBN.cfg_dtls['input_options']['converter'])
    # initiate logger
    ClassLN.initiate_logger(ClassLN, parameters_in.output_log_file, 'thm_converter')
    # define global timer to use
    t = Timer('thm',
              text      = 'Time spent is {seconds} ',
              logger    = ClassLN.logger.debug
              )
    t.start()
    # marking start of the Log
    ClassLN.logger.info('='*50)
    ClassLN.logger.info('Tableau Hyper Management started')
    # reflect input parameters given values
    ClassCLAM.listing_parameter_values(ClassCLAM, ClassLN.logger, parameters_in)
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
        ClassLN.logger.info('Given CSV file ' + parameters_in.input_file
                            + ' has been loaded into a Pandas Data Frame successfully')
        t.stop()
        t.start()
        # advanced detection of data type within Data Frame
        detected_csv_structure = ClassTD.fn_detect_csv_structure(ClassTD, ClassLN.logger,
                                                                 csv_content_df, parameters_in)
        t.stop()
        t.start()
        # create HYPER from Data Frame
        ClassTHAEL.fn_run_hyper_creation(ClassTHAEL, ClassLN.logger, csv_content_df,
                                         detected_csv_structure, parameters_in)
        t.stop()
    else:
        # doesn't exist
        ClassLN.logger.error('Given file ' + parameters_in.input_file
                             + ' does not exist, please check your inputs!')
    ClassBN.fn_final_message(ClassBN, ClassLN.logger, t, parameters_in.output_log_file)
