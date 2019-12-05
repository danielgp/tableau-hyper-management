"""
main - entry point of the package

This file is performing CSV read into HYPER file and measures time elapsed (performance)
"""
import sys
import time

from . import CommandLineArgumentsHandling as ClassCLAH
from datetime import timedelta


if __name__ == '__main__':
    # marking the start of performance measuring (in nanoseconds)
    performance_start = time.perf_counter_ns()
    ClassCLAH.fn_command_line_argument_interpretation(ClassCLAH, sys.argv[1:])
    # marking the end of performance measuring (in nanoseconds)
    performance_finish = time.perf_counter_ns()
    # calculate time spent on execution
    performance_timed = timedelta(microseconds = (performance_finish - performance_start) / 1000)
    # display time spent on execution
    print("This script has been executed in " + format(performance_timed) + ' seconds')
