import getopt
import pandas as pd
import sys
import time

from TableauHyperApiExtraLogic import TableauHyperApiExtraLogic as _cls_thael
from CommandLineArgumentsHandling import CommandLineArgumentsHandling as _cls_clah
from datetime import timedelta


def fn_command_line_argument_interpretation(argv):
    print('#'*120)
    input_file = ''
    csv_field_separator = ','
    output_file = ''
    verbose = False
    _cls_clah.fn_load_configuration(_cls_clah)
    help_feedback = __file__ + _cls_clah.fn_build_combined_options(_cls_clah)
    try:
        opts, args = getopt.getopt(argv,
                                   _cls_clah.fn_build_short_options(_cls_clah),
                                   _cls_clah.fn_build_long_options(_cls_clah))
    except getopt.GetoptError:
        print(help_feedback)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_feedback)
            sys.exit()
        elif opt in ("-i", "--input-file"):
            input_file = arg
        elif opt in ("-s", "--csv-field-separator"):
            csv_field_separator = arg
        elif opt in ("-o", "--output-file"):
            output_file = arg
        elif opt in ("-v", "--verbose"):
            verbose = True
        else:
            assert False, "Unhandled Option: " + arg
    _cls_clah.fn_assess_option(_cls_clah, 'i', input_file)
    print('CSV field separator is "' + csv_field_separator + '"')
    _cls_clah.fn_assess_option(_cls_clah, 'o', output_file)
    print('#'*120)
    csv_content_df = pd.read_csv(filepath_or_buffer = input_file,
                                 delimiter = csv_field_separator,
                                 cache_dates = True,
                                 index_col = None,
                                 memory_map = True,
                                 encoding = 'utf-8')
    _cls_thael.fn_run_hyper_creation(_cls_thael, csv_content_df, output_file, verbose)


if __name__ == '__main__':
    # marking the start of performance measuring (in nanoseconds)
    performance_start = time.perf_counter_ns()
    fn_command_line_argument_interpretation(sys.argv[1:])
    # marking the end of performance measuring (in nanoseconds)
    performance_finish = time.perf_counter_ns()
    performance_timed = timedelta(microseconds=(performance_finish - performance_start)/1000)
    print("This script has been executed in " + format(performance_timed) + ' seconds')
