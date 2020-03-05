"""
main - entry point of the package

This file is performing CSV read into HYPER file and measures time elapsed (performance)
"""

# standard Python packages
import os.path as os_path
import time
from datetime import timedelta

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
    # marking the start of performance measuring (in nanoseconds)
    performance_start = time.perf_counter_ns()
    ClassBN.fn_load_configuration(ClassBN)
    parameters_in = ClassCLAM.parse_arguments(ClassCLAM, ClassBN.cfg_dtls['options'])
    # initiate logger
    ClassLN.initiate_logger(ClassLN, parameters_in.output_log_file)
    # marking start of the Log
    ClassLN.logger.info('='*50)
    ClassLN.logger.info('Tableau Hyper Management started')
    ClassLN.logger.info('~'*50)
    ClassLN.logger.info('Input file is ' + parameters_in.input_file)
    ClassLN.logger.info('CSV field separator is ' + parameters_in.csv_field_separator)
    ClassLN.logger.info('Unique values to analyze is limited to '
                        + str(parameters_in.unique_values_to_analyze_limit))
    ClassLN.logger.info('Output file is ' + parameters_in.output_file)
    ClassLN.logger.info('~'*50)
    # initiate Data Frame from specified CSV file
    if os_path.isfile(parameters_in.input_file):
        # exists
        csv_content_df = pd.read_csv(filepath_or_buffer=parameters_in.input_file,
                                     delimiter=parameters_in.csv_field_separator,
                                     cache_dates=True,
                                     index_col=None,
                                     memory_map=True,
                                     encoding='utf-8')
        # advanced detection of data type within Data Frame
        detected_csv_structure = ClassTD.fn_detect_csv_structure(ClassTD, ClassLN.logger,
                                                                 csv_content_df, parameters_in)
        # create HYPER from Data Frame
        ClassTHAEL.fn_run_hyper_creation(ClassTHAEL, ClassLN.logger, csv_content_df,
                                         detected_csv_structure, parameters_in)
    else:
        # doesn't exist
        ClassLN.logger.error('Given file ' + parameters_in.input_file
                             + ' does not exist, please check your inputs!')
    # marking the end of performance measuring (in nanoseconds)
    performance_finish = time.perf_counter_ns()
    # calculate time spent on execution
    performance_timed = timedelta(microseconds=((performance_finish - performance_start) / 1000))
    # display time spent on execution
    ClassLN.logger.info('This session took ' + format(performance_timed) + ' to complete')
    if parameters_in.output_log_file != 'None':
        print('Application finished, please check ' + parameters_in.output_log_file)
