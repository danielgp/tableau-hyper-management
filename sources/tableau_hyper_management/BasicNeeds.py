"""
BasicNeeds - useful functions library

This library has functions useful to keep main logic short and simple
"""
# package to handle date and times
from datetime import datetime, timedelta
# package to add support for multi-language (i18n)
import gettext
# package to handle files/folders and related metadata/operations
import os
# package regular expressions
import re


class BasicNeeds:
    locale = None

    def __init__(self, in_language='en_US'):
        file_parts = os.path.normpath(os.path.abspath(__file__)).replace('\\', os.path.altsep)\
            .split(os.path.altsep)
        locale_domain = file_parts[(len(file_parts)-1)].replace('.py', '')
        locale_folder = os.path.normpath(os.path.join(
            os.path.join(os.path.altsep.join(file_parts[:-2]), 'project_locale'), locale_domain))
        self.locale = gettext.translation(locale_domain, localedir=locale_folder,
                                          languages=[in_language], fallback=True)

    def fn_add_value_to_dictionary(self, in_list, adding_value, adding_type, reference_column):
        add_type = adding_type.lower()
        total_columns = len(in_list.copy())
        reference_indexes = {
            'add': {'after': 0, 'before': 0},
            'cycle_down_to': {'after': 0, 'before': 0}
        }
        if reference_column is not None:
            reference_indexes = {
                'add': {
                    'after': in_list.copy().index(reference_column) + 1,
                    'before': in_list.copy().index(reference_column),
                },
                'cycle_down_to': {
                    'after': in_list.copy().index(reference_column),
                    'before': in_list.copy().index(reference_column),
                }
            }
        positions = {
            'after': {
                'cycle_down_to': reference_indexes.get('cycle_down_to').get('after'),
                'add': reference_indexes.get('add').get('after'),
            },
            'before': {
                'cycle_down_to': reference_indexes.get('cycle_down_to').get('before'),
                'add': reference_indexes.get('add').get('before'),
            },
            'first': {
                'cycle_down_to': 0,
                'add': 0,
            },
            'last': {
                'cycle_down_to': total_columns,
                'add': total_columns,
            }
        }
        return self.add_value_to_dictionary_by_position({
            'adding_value': adding_value,
            'list': in_list.copy(),
            'position_to_add': positions.get(add_type).get('add'),
            'position_to_cycle_down_to': positions.get(add_type).get('cycle_down_to'),
            'total_columns': total_columns,
        })

    @staticmethod
    def add_value_to_dictionary_by_position(adding_dictionary):
        list_with_values = adding_dictionary['list']
        list_with_values.append(adding_dictionary['total_columns'])
        for counter in range(adding_dictionary['total_columns'],
                             adding_dictionary['position_to_cycle_down_to'], -1):
            list_with_values[counter] = list_with_values[(counter - 1)]
        list_with_values[adding_dictionary['position_to_add']] = adding_dictionary['adding_value']
        return list_with_values

    def fn_check_inputs(self, input_parameters):
        if input_parameters.output_log_file not in (None, 'None'):
            # checking log folder first as there's all further messages will be stored
            self.fn_timestamped_print(self.locale.gettext(
                'Checking if provided folder for the log file is valid'))
            self.fn_validate_single_value(
                    os.path.dirname(input_parameters.output_log_file), 'folder')

    @staticmethod
    def fn_decide_by_omission_or_specific_true(in_dictionary, key_decision_factor):
        """
        Evaluates if a property is specified in a Dict structure

        @param in_dictionary: input Dict structure
        @param key_decision_factor: key used to search value in Dict structure
        @return: True|False
        """
        final_decision = False
        if key_decision_factor in in_dictionary:
            final_decision = True
        elif in_dictionary[key_decision_factor]:
            final_decision = True
        return final_decision

    @staticmethod
    def fn_evaluate_dict_values(in_dict):
        true_counted = 0
        for crt_value in in_dict:
            if in_dict[crt_value]:
                true_counted += 1
        all_true = False
        if true_counted == len(in_dict):
            all_true = True
        return all_true

    @staticmethod
    def fn_evaluate_list_values(in_list):
        true_counted = 0
        for crt_value in in_list:
            if crt_value:
                true_counted += 1
        all_true = False
        if true_counted == len(in_list):
            all_true = True
        return all_true

    def fn_final_message(self, local_logger, log_file_name, performance_in_seconds):
        total_time_string = str(timedelta(seconds=performance_in_seconds))
        if log_file_name == 'None':
            self.fn_timestamped_print(self.locale.gettext(
                'Application finished, whole script took {total_time_string}')
                                      .replace('{total_time_string}', total_time_string))
        else:
            local_logger.info(self.locale.gettext('Total execution time was {total_time_string}')
                              .replace('{total_time_string}', total_time_string))
            self.fn_timestamped_print(self.locale.gettext(
                'Application finished, for complete logged details please check {log_file_name}')
                                      .replace('{log_file_name}', log_file_name))

    @staticmethod
    def fn_multi_line_string_to_single(input_string):
        string_to_return = input_string.replace('\n', ' ').replace('\r', ' ')
        return re.sub(r'\s{2,100}', ' ', string_to_return).replace(' , ', ', ').strip()

    @staticmethod
    def fn_numbers_with_leading_zero(input_number_as_string, digits):
        final_number = input_number_as_string
        if len(input_number_as_string) < digits:
            final_number = '0' * (digits - len(input_number_as_string)) + input_number_as_string
        return final_number

    def fn_optional_print(self, boolean_variable, string_to_print):
        if boolean_variable:
            self.fn_timestamped_print(string_to_print)

    @staticmethod
    def fn_timestamped_print(string_to_print):
        print(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f %Z") + '- ' + string_to_print)

    def fn_validate_one_value(self, value_to_validate, validation_type):
        is_invalid = False
        message = ''
        if validation_type == 'file':
            is_invalid = (not os.path.isfile(value_to_validate))
            message = self.locale.gettext('Given file "{value_to_validate}" does not exist')
        elif validation_type == 'folder':
            is_invalid = (not os.path.isdir(value_to_validate))
            message = self.locale.gettext('Given folder "{value_to_validate}" does not exist')
        elif validation_type == 'url':
            url_reg_expression = 'https?://(?:www)?(?:[\\w-]{2,255}(?:\\.\\w{2,66}){1,2})'
            is_invalid = (not re.match(url_reg_expression, value_to_validate))
            message = self.locale.gettext('Given url "{value_to_validate}" is not valid')
        return {
            'is_invalid': is_invalid,
            'message': message.replace('{value_to_validate}', value_to_validate),
        }

    def fn_validate_single_value(self, value_to_validate, validation_type):
        validation_details = self.fn_validate_one_value(value_to_validate, validation_type)
        if validation_details['is_invalid']:
            self.fn_timestamped_print(validation_details['message'])
            exit(1)
