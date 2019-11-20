import getopt
import sys
import time

from TableauHyperApiExtraLogic import TableauHyperApiExtraLogic
from datetime import timedelta


def fn_command_line_argument_interpretation(argv):
    input_file = ''
    csv_field_separator = ''
    output_file = ''
    verbose = False
    print('#'*120)
    try:
        opts, args = getopt.getopt(argv, "hi:cfs:o:v:", [
            "input-file=", 
            "csv-field-separator=", 
            "output-file=",
            "verbose"
        ])
    except getopt.GetoptError:
        print('main.py -i|--input-file <input-file>'
            + ' -cfs|--csv-field-separator <csv-field-separator>'
            + ' -o|--output-file <output-file>'
            + ' [-v|--verbose]'
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -i|--input-file <input-file>'
            + ' -cfs|--csv-field-separator <csv-field-separator>'
            + ' -o|--output-file <output-file>')
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
    if csv_field_separator == '':
        print('Fatal Error........................................................................................:-(')
        print('Expected -cs|--csv-field-separator <csv-field-separator> but nothing of that sort has been seen... :-(')
        sys.exit(2)
    else:
        print('CSV field separator is "' + csv_field_separator + '"')
    if output_file == '':
        print('Fatal Error.......................................................................:-(')
        print('Expected -o|--output-file <output-file> but nothing of that sort has been seen... :-(')
        sys.exit(2)
    else:
        print('Output file is "' + output_file + '"')
    print('#'*120)
    # marking the start of performance measuring (in nanoseconds)
    performance_start = time.perf_counter_ns()
    TableauHyperApiExtraLogic.fn_run_create_hyper_file_from_csv(input_file,
                                                                csv_field_separator,
                                                                output_file,
                                                                verbose)
    performance_finish = time.perf_counter_ns()
    performance_timed = timedelta(microseconds=(performance_finish - performance_start)/1000)
    print("This script has been executed in " + format(performance_timed) + ' seconds')


if __name__ == '__main__':
    fn_command_line_argument_interpretation(sys.argv[1:])
