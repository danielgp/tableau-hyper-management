"""
Class Parameter Handling

Facilitates handling parameters values
"""
# package to handle date and times
from datetime import datetime, timedelta
# package to allow year and/or month operations based on a reference date
import datedelta
# package to add support for multi-language (i18n)
import gettext
# package to perform mathematical operations
import math
# package to handle files/folders and related metadata/operations
import os
# package regular expressions
import re


class ParameterHandling:
    known_expressions = {
        'year': ['CY', 'CurrentYear'],
        'semester': ['CYCS', 'CurrentYearCurrentSemester'],
        'semester_week': ['CYCSCW', 'CurrentYearCurrentSemesterCurrentWeek'],
        'just_semester': ['CS', 'CurrentSemester'],
        'quarter': ['CYCQ', 'CurrentYearCurrentQuarter'],
        'quarter_week': ['CYCQCW', 'CurrentYearCurrentQuarterCurrentWeek'],
        'just_quarter': ['CQ', 'CurrentQuarter'],
        'fiscal_period': ['CYCFP', 'CurrentYearCurrentFiscalPeriod'],
        'just_fiscal_period': ['CFP', 'FiscalPeriod'],
        'month': ['CYCM', 'CurrentYearCurrentMonth'],
        'just_month': ['CM', 'CurrentMonth'],
        'week': ['CYCW', 'CurrentYearCurrentWeek'],
        'just_week': ['CW', 'CurrentWeek'],
        'day': ['CYCMCD', 'CurrentYearCurrentMonthCurrentDay'],
        'just_day': ['CD', 'CurrentDay'],
        'hour': ['CYCMCDCH', 'CurrentYearCurrentMonthCurrentDayCurrentHour'],
    }
    output_standard_formats = {
        'year': '%Y',
        'fiscal_period': '%Y0%m',
        'just_fiscal_period': '0%m',
        'month': '%Y%m',
        'just_month': '%m',
        'day': '%Y%m%d',
        'just_day': '%d',
        'hour': '%Y%m%d%H%M%S%f',
    }
    locale = None

    def __init__(self, in_language='en_US'):
        file_parts = os.path.normpath(os.path.abspath(__file__)).replace('\\', os.path.altsep) \
            .split(os.path.altsep)
        locale_domain = file_parts[(len(file_parts) - 1)].replace('.py', '')
        locale_folder = os.path.normpath(os.path.join(
            os.path.join(os.path.altsep.join(file_parts[:-2]), 'project_locale'), locale_domain))
        self.locale = gettext.translation(locale_domain, localedir=locale_folder,
                                          languages=[in_language], fallback=True)

    def build_parameters(self, local_logger, query_session_parameters, in_parameter_rules
                         , in_start_iso_weekday):
        local_logger.debug(self.locale.gettext('Seen Parameters are: {parameters}')
                           .replace('{parameters}', str(query_session_parameters)))
        parameters_type = type(query_session_parameters)
        local_logger.debug(self.locale.gettext('Parameters type is {parameter_type}')
                           .replace('{parameter_type}', str(parameters_type)))
        tp = None
        if parameters_type == dict:
            tp = tuple(query_session_parameters.values())
        elif parameters_type == list:
            tp = tuple(query_session_parameters)
        else:
            local_logger.error(self.locale.gettext(
                'Unexpected parameter type, either Dictionary or List expected, '
                + 'but seen is {parameter_type}')
                               .replace('{parameter_type}', str(parameters_type)))
            exit(1)
        local_logger.debug(self.locale.gettext(
            'Initial Tuple for Parameters is: {parameters_tuple}')
                           .replace('{parameters_tuple}', str(tp)))
        return self.stringify_parameters(local_logger, tp, in_parameter_rules, in_start_iso_weekday)

    @staticmethod
    def calculate_date_deviation(in_date, deviation_type, expression_parts):
        if expression_parts[2] is None:
            expression_parts[2] = 0
        final_dates = {
            'year': in_date + datedelta.datedelta(years=int(expression_parts[2])),
            'semester': in_date + timedelta(weeks=(int(expression_parts[2]) * 26)),
            'semester_week': in_date + timedelta(weeks=int(expression_parts[2])),
            'quarter': in_date + datedelta.datedelta(days=(int(expression_parts[2]) * 90)),
            'quarter_week': in_date + timedelta(weeks=int(expression_parts[2])),
            'fiscal_period': in_date + datedelta.datedelta(months=int(expression_parts[2])),
            'month': in_date + datedelta.datedelta(months=int(expression_parts[2])),
            'week': in_date + timedelta(weeks=int(expression_parts[2])),
            'day': in_date + timedelta(days=int(expression_parts[2])),
            'hour': in_date + timedelta(hours=int(expression_parts[2])),
        }
        return final_dates.get(deviation_type)

    def calculate_date_from_expression(self, local_logger, expression_parts, in_start_iso_weekday):
        final_string = ''
        all_known_expressions = self.get_flattened_known_expressions()
        if expression_parts[1] in all_known_expressions:
            str_expression = '_'.join(expression_parts)
            local_logger.debug(self.locale.gettext(
                'A known expression "{expression_parts}" has to be interpreted')
                               .replace('{expression_parts}', str_expression))
            final_string = self.interpret_known_expression(
                datetime.now(), expression_parts, in_start_iso_weekday)
            local_logger.debug(self.locale.gettext(
                'Known expression "{expression_parts}" has been interpreted as {final_string}')
                               .replace('{expression_parts}', str_expression)
                               .replace('{final_string}', final_string))
        else:
            local_logger.debug(self.locale.gettext(
                'Unknown expression encountered: provided was "{given_expression}" '
                + 'which is not among known ones: "{all_known_expressions}"')
                               .replace('{given_expression}', str(expression_parts[1]))
                               .replace('{all_known_expressions}',
                                        '", "'.join(all_known_expressions)))
            exit(1)
        return final_string

    def eval_expression(self, local_logger, crt_parameter, in_start_iso_weekday):
        value_to_return = crt_parameter
        reg_ex = re.search(r'(CalculatedDate_[A-Za-z]{2,75}_*(-*)[0-9]{0,2})', crt_parameter)
        if reg_ex:
            parameter_value_parts = reg_ex.group().split('_')
            calculated = self.calculate_date_from_expression(
                local_logger, parameter_value_parts, in_start_iso_weekday)
            value_to_return = re.sub(reg_ex.group(), calculated, crt_parameter)
            local_logger.debug(self.locale.gettext(
                'Current Parameter is STR and has been re-interpreted as value: "{str_value}"')
                               .replace('{str_value}', str(value_to_return)))
        return value_to_return

    def get_child_parent_expressions(self):
        child_parent_values = {}
        for current_expression_group in self.known_expressions.items():
            for current_expression in current_expression_group[1]:
                child_parent_values[current_expression] = current_expression_group[0]
        return child_parent_values

    def get_flattened_known_expressions(self):
        flat_values = []
        for crt_list in self.known_expressions.values():
            flat_values += crt_list
        return flat_values

    @staticmethod
    def get_week_number_as_two_digits_string(in_date, in_start_iso_weekday=1):
        if in_start_iso_weekday == 7:
            in_date = in_date + timedelta(days=1)
        week_iso_num = datetime.isocalendar(in_date)[1]
        iso_wek_to_return = str(week_iso_num)
        if week_iso_num < 10:
            iso_wek_to_return = '0' + iso_wek_to_return
        return str(datetime.isocalendar(in_date)[0]), iso_wek_to_return

    def handle_query_parameters(self, local_logger, given_session, in_start_iso_weekday):
        tp = None
        if 'parameters' in given_session:
            parameter_rules = []
            if 'parameters-handling-rules' in given_session:
                parameter_rules = given_session['parameters-handling-rules']
            tp = self.build_parameters(
                local_logger, given_session['parameters'], parameter_rules,
                in_start_iso_weekday)
        return tp

    def interpret_known_expression(self, ref_date, expression_parts, in_start_iso_weekday):
        child_parent_expressions = self.get_child_parent_expressions()
        deviation_original = child_parent_expressions.get(expression_parts[1])
        deviation = deviation_original.replace('just_', '')
        finalized_date = ref_date
        if len(expression_parts) > 2:
            finalized_date = self.calculate_date_deviation(ref_date, deviation, expression_parts)
        if deviation_original in ('just_semester', 'just_quarter', 'just_week',
                                  'semester', 'semester_week', 'quarter', 'quarter_week', 'week'):
            year_number_string, week_number_string = self.get_week_number_as_two_digits_string(
                finalized_date, in_start_iso_weekday)
            # to ensure less than 4 days within last week of year r reported to next year (ISO)
            semester_year_string = str(math.ceil(int(week_number_string) / 26))
            quarter_string = str(min(int(week_number_string),
                                     math.ceil(int(datetime.strftime(finalized_date, '%m')) / 3)))
            # values pre-calculated
            values_to_pick = {
                'just_semester': 'H' + semester_year_string,
                'just_quarter': 'Q' + quarter_string,
                'just_week': week_number_string,
                'semester': year_number_string + 'H' + semester_year_string,
                'semester_week': year_number_string + 'H' + semester_year_string
                                 + 'wk' + week_number_string,
                'quarter': str(datetime.strftime(finalized_date, '%Y')) + 'Q' + quarter_string,
                'quarter_week': year_number_string + 'Q' + quarter_string
                                + 'wk' + week_number_string,
                'week': year_number_string + week_number_string,
            }
            final_string = values_to_pick.get(deviation_original)
        else:
            final_string = datetime.strftime(
                finalized_date, self.output_standard_formats.get(deviation_original))
        return final_string

    def manage_parameter_value(self, in_logger, in_prefix, in_parameter, in_parameter_rules):
        element_to_join = ''
        if in_prefix == 'dict':
            element_to_join = in_parameter.values()
        elif in_prefix == 'list':
            element_to_join = in_parameter
        in_logger.debug(self.locale.gettext(
            'Current Parameter is {parameter_type} and has the value: "{str_value}"')
                        .replace('{parameter_type}', self.locale.gettext(in_prefix.upper()))
                        .replace('{str_value}', str(element_to_join)))
        return in_parameter_rules[in_prefix + '-values-prefix'] \
               + in_parameter_rules[in_prefix + '-values-glue'].join(element_to_join) \
               + in_parameter_rules[in_prefix + '-values-suffix']

    @staticmethod
    def set_default_starting_weekday(in_dict):
        week_starts_with_iso_weekday = 1
        if 'start-iso-weekday' in in_dict['session']:
            if in_dict['session']['start-iso-weekday'] == 'inherit-from-parent':
                in_dict['session']['start-iso-weekday'] = in_dict['query']['start-iso-weekday']
            elif in_dict['session']['start-iso-weekday'] == 'inherit-from-grand-parent':
                in_dict['session']['start-iso-weekday'] = in_dict['sequence']['start-iso-weekday']
            week_starts_with_iso_weekday = in_dict['session']['start-iso-weekday']
        return week_starts_with_iso_weekday

    def simulate_final_query(self, local_logger, timer, in_query, in_parameters_number, in_tp):
        timer.start()
        return_query = in_query
        if in_parameters_number > 0:
            try:
                return_query = in_query % in_tp
            except TypeError as e:
                local_logger.error(self.locale.gettext(
                    'Initial query expects {expected_parameters_counted} '
                    + 'but only {given_parameters_counted} were provided')
                                   .replace('{expected_parameters_counted}',
                                            str(in_parameters_number))
                                   .replace('{given_parameters_counted}', str(len(in_tp))))
                local_logger.error(e)
        timer.stop()
        return return_query

    def stringify_parameters(self, local_logger, tuple_parameters, given_parameter_rules,
                             in_start_iso_weekday):
        working_list = []
        for ndx, crt_parameter in enumerate(tuple_parameters):
            current_parameter_type = type(crt_parameter)
            working_list.append(ndx)
            if current_parameter_type == str:
                local_logger.debug(self.locale.gettext(
                    'Current Parameter is {parameter_type} and has the value: "{str_value}"')
                                   .replace('{parameter_type}', self.locale.gettext('STR'))
                                   .replace('{str_value}', crt_parameter))
                working_list[ndx] = self.eval_expression(
                    local_logger, crt_parameter, in_start_iso_weekday)
            elif current_parameter_type in (list, dict):
                prefix = str(current_parameter_type).replace("<class '", '').replace("'>", '')
                working_list[ndx] = self.manage_parameter_value(
                    local_logger, prefix.lower(), crt_parameter, given_parameter_rules)
        final_tuple = tuple(working_list)
        local_logger.debug(self.locale.gettext('Final Tuple for Parameters is: {final_tuple}')
                           .replace('{final_tuple}', str(final_tuple)))
        return final_tuple
