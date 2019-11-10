import csv
import re
########################################################################################################################
file_path = 'C:\\www\\Data\\GitRepositories\\BitBucket\\AutomatedUnitTesting\\tests\\DataDump\\'
file_name = file_path + 'Budget_Forecast_Actual__Summary.csv'
decimal_separator = '.'
thousand_separator = '-'
########################################################################################################################


def type_determination(variable_to_assess):
    # https://regex101.com/
    re_float = '^[0-9]*\\' + decimal_separator + '{1}[0-9]*$'
    re_date = '^(1[0-9]{3}|2[0-9]{3})-(0[0-9]|1[0-2])-([0-5][0-9])$'
    re_time = '^(2[0-3]|[01][0-9]|[0-9]):([0-5][0-9]|[0-9]):([0-5][0-9]|[0-9])$'
    if re.match('^[0-9]+$', variable_to_assess):
        return 'int'
    elif re.match(re_float, variable_to_assess):
        return 'float'
    elif re.match(re_date, variable_to_assess):
        return 'date-iso8601'
    elif re.match(re_time, variable_to_assess):
        return 'time'
    elif re.match(re_date[:-1] + ' ' + re_time[1:], variable_to_assess):
        return 'datetime-iso8601'
    elif isinstance(variable_to_assess, str):
        return 'str'
    else:
        return 'unknown'


########################################################################################################################
col_to_analyze = 14
########################################################################################################################
with open(file_name, newline='') as csv_file:
    csv_object = csv.DictReader(csv_file, delimiter=';')
    print(csv_object.fieldnames)
    for row_idx, row_content in enumerate(csv_object):
        if row_idx <= 10:
            print('[' + csv_object.fieldnames[col_to_analyze] + '] on row ' + str(row_idx)
                + ' is ' + row_content[csv_object.fieldnames[col_to_analyze]]
                + ' and that means type '
                + type_determination(row_content[csv_object.fieldnames[col_to_analyze]]))
