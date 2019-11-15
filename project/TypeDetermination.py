import csv
import re


class TypeDetermination:

    importance__low_to_high = [
        'empty',
        'int',
        'float-USA',
        'date-iso8601',
        'date-USA',
        'time-24',
        'time-24-us',
        'time-USA',
        'time-USA-us',
        'datetime-iso8601',
        'datetime-iso8601-us',
        'str'
    ]

    def fn_detect_csv_structure(given_file_name, csv_field_separator, verbose):
        csv_structure = []
        with open(given_file_name, newline='') as csv_file:
            csv_object = csv.DictReader(csv_file, delimiter=';')
            # parse rows with index
            for row_idx, row_content in enumerate(csv_object):
                # limit rows evaluation to a certain value
                if row_idx <= 200:
                    print_prefix = 'On the row ' + str((row_idx + 1))
                    # parse all columns with index
                    for col_idx, column_name in enumerate(csv_object.fieldnames):
                        # determine the field type by current row and column content
                        crt_field_type = TypeDetermination.\
                            fn_type_determination(row_content[csv_object.fieldnames[col_idx]])
                        # evaluate if CSV structure for current field (column) already exists
                        if row_idx > 0:
                            '''
                            if CSV structure for current field (column) exists, 
                            does the current type is more important?
                            '''
                            crt_type_index = TypeDetermination.importance__low_to_high.index(crt_field_type)
                            prv_type_index = TypeDetermination.importance__low_to_high.\
                                index(csv_structure[col_idx]['type'])
                            if crt_type_index > prv_type_index:
                                if verbose:
                                    print(print_prefix 
                                        + ' column ' + str(col_idx)
                                        + ' having the name [' + csv_object.fieldnames[col_idx] + '] '
                                        + ' has the value <' + row_content[csv_object.fieldnames[col_idx]]
                                        + '> which means is of type "' + crt_field_type + '" '
                                        + ' and that is stronger than previously thought to be as "'
                                        + csv_structure[col_idx]['type'] + '"')
                                csv_structure[col_idx]['type'] = crt_field_type
                        else:
                            csv_structure.append(col_idx)
                            csv_structure[col_idx] = {
                                'order': col_idx,
                                'name': csv_object.fieldnames[col_idx],
                                'type': crt_field_type
                            }
                            if crt_field_type == 'str':
                                csv_structure[col_idx]['length'] = len(row_content[csv_object.fieldnames[col_idx]])
                            if verbose:
                                print(print_prefix + ' column ' + str(col_idx)
                                    + ' having the name [' + csv_object.fieldnames[col_idx] + '] '
                                    + ' has the value <' + row_content[csv_object.fieldnames[col_idx]]
                                    + '> which mean is of type "' + crt_field_type + '"')
        return csv_structure

    @staticmethod
    def fn_type_determination(variable_to_assess):
        # Website https://regex101.com/ was used to validate below code
        re_int = '^[+-]*[0-9]+$'
        re_float = '^[+-]*[0-9]*\\.{1}[0-9]*$'
        re_date_us = '^([1-9]|11|12|0[0-9]|1[0-2])/([1-9]|0[0-9]|1[0-9]|2[0-9]|3[0-1])/(1[0-9]{3}|2[0-9]{3})$'
        re_date_iso8601 = '^(1[0-9]{3}|2[0-9]{3})-([0-9]|0[0-9]|1[0-2])-([0-9]|0[0-9]|1[0-9]|2[0-9]|3[0-1])$'
        re_time24 = '^(2[0-3]|[01][0-9]|[0-9]):([0-5][0-9]|[0-9]):([0-5][0-9]|[0-9])$'
        re_time_us = '^([0-9]|0[0-9]|1[0-2]):{1}([0-5][0-9]|[0-9]):{1}([0-5][0-9]|[0-9])\\s*(AM|am|PM|pm)$'
        if variable_to_assess == '':
            return 'empty'
        elif re.match(re_int, variable_to_assess):
            return 'int'
        elif re.match(re_float, variable_to_assess):
            return 'float-US'
        elif re.match(re_date_iso8601, variable_to_assess):
            return 'date-iso8601'
        elif re.match(re_date_us, variable_to_assess):
            return 'date-USA'
        elif re.match(re_time24, variable_to_assess):
            return 'time-24'
        elif re.match(re_time24.replace(')$', ').([0-9]{6})$'), variable_to_assess):
            return 'time-24-us'
        elif re.match(re_time_us, variable_to_assess):
            return 'time-USA'
        elif re.match(re_time_us.replace(')$', ').([0-9]{6})$'), variable_to_assess):
            return 'time-USA-us'
        elif re.match(re_date_iso8601[:-1] + ' ' + re_time24[1:], variable_to_assess):
            return 'datetime-iso8601'
        elif re.match(re_date_iso8601[:-1] + ' ' + re_time24[1:].replace(')$', ').([0-9]{6})$'), variable_to_assess):
            return 'datetime-iso8601-us'
        else:
            return 'str'
