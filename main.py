"""
main - entry point of the package

This file is performing CSV read into HYPER file and measures time elapsed (performance)
"""

# standard Python packages
import time
from datetime import timedelta

# additional packages to be installed from PyPi
import pandas as pd

# Custom classes specific to this package
from tableau_hyper_management.TypeDetermination import ClassBN as ClsBN
from tableau_hyper_management.TypeDetermination import TypeDetermination as ClassTD
from tableau_hyper_management.CommandLineArgumentsManagement import \
    CommandLineArgumentsManagement as ClassCLAM
from tableau_hyper_management.TableauHyperApiExtraLogic import \
    TableauHyperApiExtraLogic as ClassTHAEL

# main execution logic
if __name__ == '__main__':
    # marking the start of performance measuring (in nanoseconds)
    performance_start = time.perf_counter_ns()
    ClsBN.fn_load_configuration(ClsBN)
    parameters_interpreted = ClassCLAM.parse_arguments(ClassCLAM, ClsBN.cfg_dtls['options'])
    print('~'*100)
    ClsBN.fn_timestamped_print(ClsBN, 'Input file is ' + parameters_interpreted.input_file)
    ClsBN.fn_timestamped_print(ClsBN, 'CSV field separator is '
                               + parameters_interpreted.csv_field_separator)
    ClsBN.fn_timestamped_print(ClsBN, 'Unique values to analyze is limited to '
                               + str(parameters_interpreted.unique_values_to_analyze_limit))
    ClsBN.fn_timestamped_print(ClsBN, 'Output file is ' + parameters_interpreted.output_file)
    print('~' * 100)
    # initiate Data Frame from specified CSV file
    csv_content_df = pd.read_csv(filepath_or_buffer=parameters_interpreted.input_file,
                                 delimiter=parameters_interpreted.csv_field_separator,
                                 cache_dates=True,
                                 index_col=None,
                                 memory_map=True,
                                 encoding='utf-8')
    # advanced detection of data type within Data Frame
    detected_csv_structure = ClassTD.fn_detect_csv_structure(ClassTD, csv_content_df,
                                                             parameters_interpreted)
    # create HYPER from Data Frame
    ClassTHAEL.fn_run_hyper_creation(ClassTHAEL, csv_content_df, detected_csv_structure,
                                     parameters_interpreted)
    # marking the end of performance measuring (in nanoseconds)
    performance_finish = time.perf_counter_ns()
    # calculate time spent on execution
    performance_timed = timedelta(microseconds=((performance_finish - performance_start) / 1000))
    # display time spent on execution
    ClsBN.fn_timestamped_print(ClsBN, 'This script has been executed in '
                               + format(performance_timed) + ' seconds')
