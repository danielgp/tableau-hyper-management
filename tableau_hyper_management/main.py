"""
main - entry point of the package

This file is performing CSV read into HYPER file and measures time elapsed (performance)
"""
# standard Python packages
import time
from datetime import timedelta
# Custom classes specific to this package
from CommandLineArgumentsHandling import ClassBN
from CommandLineArgumentsHandling import CommandLineArgumentsHandling as ClassCLAH
# main execution logic
if __name__ == '__main__':
    # marking the start of performance measuring (in nanoseconds)
    performance_start = time.perf_counter_ns()
    ClassCLAH.fn_command_line_argument_interpretation(ClassCLAH)
    # marking the end of performance measuring (in nanoseconds)
    performance_finish = time.perf_counter_ns()
    # calculate time spent on execution
    performance_timed = timedelta(microseconds=((performance_finish - performance_start) / 1000))
    # display time spent on execution
    ClassBN.fn_timestamped_print(ClassBN, 'This script has been executed in '
                                 + format(performance_timed) + ' seconds')
