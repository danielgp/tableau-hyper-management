import re


class TypeDetermination:

    importance__low_to_high = [
        'empty',
        'int',
        'float-US',
        'date-iso8601',
        'time24',
        'timeUS',
        'datetime-iso8601',
        'str'
    ]

    @staticmethod
    def type_determination(variable_to_assess):
        # Website https://regex101.com/ was used to validate below code
        re_float = '^[+-]*[0-9]*\\.{1}[0-9]*$'
        re_date = '^(1[0-9]{3}|2[0-9]{3})-(0[0-9]|1[0-2])-([0-5][0-9])$'
        re_time24 = '^(2[0-3]|[01][0-9]|[0-9]):([0-5][0-9]|[0-9]):([0-5][0-9]|[0-9])$'
        re_time_usa = '^([0-9]|0[0-9]|1[0-2]):{1}([0-5][0-9]|[0-9]):{1}([0-5][0-9]|[0-9])\\s*(AM|am|PM|pm)$'
        if variable_to_assess == '':
            return 'empty'
        elif re.match('^[+-]*[0-9]+$', variable_to_assess):
            return 'int'
        elif re.match(re_float, variable_to_assess):
            return 'float-US'
        elif re.match(re_date, variable_to_assess):
            return 'date-iso8601'
        elif re.match(re_time24, variable_to_assess):
            return 'time24'
        elif re.match(re_time_usa, variable_to_assess):
            return 'timeUS'
        elif re.match(re_date[:-1] + ' ' + re_time24[1:], variable_to_assess):
            return 'datetime-iso8601'
        else:
            return 'str'
