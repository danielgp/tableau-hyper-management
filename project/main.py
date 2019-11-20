import getopt
import sys
import time

from TableauHyperApiExtraLogic import TableauHyperApiExtraLogic
from CommandLineArgumentsHandling import CommandLineArgumentsHandling as _clah
from datetime import timedelta


def fn_command_line_argument_interpretation(argv):
    print('#'*120)
    _clah.fn_load_configuration(_clah)
    input_file = ''
    csv_field_separator = ','
    output_file = ''
    verbose = False
    help_feedback = __file__ + _clah.fn_build_combined_options(_clah)
    try:
        opts, args = getopt.getopt(argv,  _clah.fn_build_short_options(_clah), _clah.fn_build_long_options(_clah))
    except getopt.GetoptError:
        print(help_feedback)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_feedback)
            sys.exit()
        elif opt in ("-i", "--input-file"):
            input_file = arg
        elif opt in ("-cfs", "--csv-field-separator"):
            csv_field_separator = arg
        elif opt in ("-o", "--output-file"):
            output_file = arg
        elif opt in ("-v", "--verbose"):
            verbose = True
        else:
            assert False, "unhandled option"
    if input_file == '':
        print('Fatal Error.....................................................................:-(')
        print('Expected -i|--input-file <input-file> but nothing of that sort has been seen... :-(')
        sys.exit(2)
    else:
        print('Input file is "' + input_file + '"')
    print('CSV field separator is "' + csv_field_separator + '"')
    if output_file == '':
        print('Fatal Error.......................................................................:-(')
        print('Expected -o|--output-file <output-file> but nothing of that sort has been seen... :-(')
        sys.exit(2)
    else:
        print('Output file is "' + output_file + '"')
    print('#'*120)
    TableauHyperApiExtraLogic.fn_run_create_hyper_file_from_csv(input_file,
                                                                csv_field_separator,
                                                                output_file,
                                                                verbose)


if __name__ == '__main__':
    # marking the start of performance measuring (in nanoseconds)
    performance_start = time.perf_counter_ns()
    fn_command_line_argument_interpretation(sys.argv[1:])
    # marking the end of performance measuring (in nanoseconds)
    performance_finish = time.perf_counter_ns()
    performance_timed = timedelta(microseconds=(performance_finish - performance_start)/1000)
    print("This script has been executed in " + format(performance_timed) + ' seconds')
