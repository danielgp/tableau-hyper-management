"""
TableauHyperApiExtraLogic - a Hyper client library.

This library allows packaging CSV content into HYPER format with data type checks
"""
# package to add support for multi-language (i18n)
import gettext
# package to handle files/folders and related metadata/operations
import os
# package regular expression
import re
# package to handle numerical structures
import numpy
# package to handle Data Frames (in this file)
import pandas as pd
# Custom classes from Tableau Hyper package
from tableauhyperapi import HyperProcess, Telemetry, Connection, CreateMode, \
    NOT_NULLABLE, NULLABLE, SqlType, TableDefinition, TableName, Inserter, HyperException


class TableauHyperApiExtraLogic:
    locale = None
    supported_input_file_types = ('csv', 'json', 'parquet', 'pickle')
    columns_for_hyper_conversion = {}
    hyper_conversion_dtypes = ['str', 'int64', 'float']

    def __init__(self, in_language):
        file_parts = os.path.normpath(os.path.abspath(__file__)).replace('\\', os.path.altsep) \
            .split(os.path.altsep)
        locale_domain = file_parts[(len(file_parts) - 1)].replace('.py', '')
        locale_folder = os.path.normpath(os.path.join(
            os.path.join(os.path.altsep.join(file_parts[:-2]), 'project_locale'), locale_domain))
        self.locale = gettext.translation(locale_domain, localedir=locale_folder,
                                          languages=[in_language], fallback=True)

    def fn_build_hyper_columns(self, logger, timer, in_data_frame_structure):
        timer.start()
        list_to_return = []
        for current_field_structure in in_data_frame_structure:
            list_to_return.append(current_field_structure['order'])
            current_column_type = self.fn_convert_to_hyper_types(current_field_structure['type'])
            logger.debug(self.locale.gettext(
                'Column {column_order} having name [{column_name}] and type "{column_type}" '
                + 'will become "{column_type_new}"')
                         .replace('{column_order}', str(current_field_structure['order']))
                         .replace('{column_name}', current_field_structure['name'])
                         .replace('{column_type}', str(current_field_structure['type']))
                         .replace('{column_type_new}', str(current_column_type)))
            nullability_value = NULLABLE
            if current_field_structure['nulls'] == 0:
                nullability_value = NOT_NULLABLE
            list_to_return[current_field_structure['order']] = TableDefinition.Column(
                name=current_field_structure['name'],
                type=current_column_type,
                nullability=nullability_value
            )
        logger.info(self.locale.gettext('Building Hyper columns completed'))
        timer.stop()
        return list_to_return

    def fn_convert_multiple_columns(self, in_logger, timer, in_data_frame, in_target_dtype):
        # if there's a list of columns to be converted to Integer do that
        if in_target_dtype in self.columns_for_hyper_conversion:
            timer.start()
            col_to_convert = self.columns_for_hyper_conversion[in_target_dtype]
            if in_target_dtype in ('int64', 'float'):
                in_data_frame[col_to_convert] = in_data_frame[col_to_convert]\
                    .fillna(0).astype(in_target_dtype)
            else:
                in_data_frame[col_to_convert] = in_data_frame[col_to_convert]\
                    .astype(in_target_dtype)
            in_logger.info(self.locale.gettext(
                'Converting multiple columns "{column_list}" to {target_data_type} completed')
                           .replace('{column_list}', '", "'.join(col_to_convert))
                           .replace('{target_data_type}', in_target_dtype.upper()))
            timer.stop()
        return in_data_frame

    @staticmethod
    def fn_convert_to_hyper_types(given_type):
        switcher = {
            'empty': SqlType.text(),
            'bool': SqlType.bool(),
            'int': SqlType.big_int(),
            'float-dot': SqlType.double(),
            'date-YMD': SqlType.date(),
            'date-MDY': SqlType.date(),
            'date-DMY': SqlType.date(),
            'time-24': SqlType.time(),
            'time-12': SqlType.time(),
            'datetime-24-YMD': SqlType.timestamp(),
            'datetime-12-MDY': SqlType.timestamp(),
            'datetime-24-DMY': SqlType.timestamp(),
            'str': SqlType.text()
        }
        identified_type = switcher.get(given_type)
        if identified_type is None:
            identified_type = SqlType.text()
        return identified_type

    def fn_delete_data_from_hyper(self, in_logger, timer, in_dict):
        timer.start()
        in_logger.debug(self.locale.gettext(
            'Hyper SQL about to be executed is: {hyper_sql}')
                        .replace('{hyper_sql}', in_dict['sql query']))
        row_count = in_dict['connection'].execute_command(command=in_dict['query'])
        in_logger.debug(self.locale.gettext(
            'Hyper SQL executed with success and {rows_counted} have been retrieved')
                        .replace('{rows_counted}', str(row_count)))
        timer.stop()

    def fn_insert_data_into_hyper_table(self, local_logger, timer, in_dict):
        timer.start()
        # Execute the actual insert
        with Inserter(in_dict['connection'], in_dict['table']) as hyper_insert:
            hyper_insert.add_rows(rows=in_dict['data'])
            hyper_insert.execute()
        local_logger.info(self.locale.gettext('Data has been inserted into Hyper table'))
        timer.stop()

    def fn_create_hyper_schema(self, local_logger, timer, in_dict):
        timer.start()
        in_dict['connection'].catalog.create_schema(in_dict['schema name'])
        local_logger.info(self.locale.gettext(
            'Hyper schema "{hyper_schema_name}" has been created')
                          .replace('{hyper_schema_name}', in_dict['schema name']))
        timer.stop()

    def fn_create_hyper_table(self, local_logger, timer, in_dict):
        timer.start()
        out_hyper_table = TableDefinition(
            TableName(in_dict['schema name'], in_dict['table name']),
            columns=in_dict['columns'],
        )
        in_dict['connection'].catalog.create_table(table_definition=out_hyper_table)
        local_logger.info(self.locale.gettext(
            'Hyper table "{hyper_table_name}" has been created')
                          .replace('{hyper_table_name}', in_dict['table name']))
        timer.stop()
        return out_hyper_table

    def fn_get_column_names_from_table(self, in_logger, in_dict):
        columns_counted = in_dict['table definition'].column_count
        in_logger.debug(self.locale.gettext('A number of {column_count} columns were found')
                        .replace('{column_count}', str(columns_counted)))
        columns_counter = 0
        table_columns = []
        while columns_counter < columns_counted:
            table_columns.append(columns_counter)
            table_columns[columns_counter] = str(in_dict['table definition'].get_column(
                columns_counter).name).replace('"', '')
            columns_counter += 1
        in_logger.debug(self.locale.gettext('And these columns are: {column_list}')
                        .replace('{column_list}', str(table_columns)))
        return table_columns

    def fn_get_records_count_from_table(self, local_logger, timer, in_dict):
        timer.start()
        # Number of rows in the <hyper_table> table.
        # `execute_scalar_query` is for executing a query
        # that returns exactly one row with one column.
        query_to_run = 'SELECT COUNT(*) FROM "{hyper_schema_name}"."{hyper_table_name}"' \
            .replace('{hyper_schema_name}', in_dict['schema name']) \
            .replace('{hyper_table_name}', in_dict['table name'])
        row_count = in_dict['connection'].execute_scalar_query(query=query_to_run)
        local_logger.info(self.locale.gettext('Table {hyper_table_name} has {row_count} rows')
                          .replace('{hyper_schema_name}', in_dict['schema name']) \
                          .replace('{hyper_table_name}', in_dict['table name']) \
                          .replace('{row_count}', str(row_count)))
        timer.stop()

    def fn_hyper_handle(self, in_logger, timer, in_dict):
        timer.start()
        out_data_frame = None
        try:
            # Starts Hyper Process with telemetry enabled/disabled to send data to Tableau or not
            # To opt in, simply set telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU.
            # To opt out, simply set telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU.
            telemetry_chosen = Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU
            with HyperProcess(telemetry=telemetry_chosen) as hyper_process:
                in_logger.debug(self.locale.gettext('Hyper engine process initialized'))
                in_logger.debug(self.locale.gettext('Chosen Telemetry is {telemetry_value}')
                                .replace('{telemetry_value}', str(telemetry_chosen)))
                timer.stop()
                timer.start()
                hyper_create_mode = {
                    'append': CreateMode.NONE,
                    'overwrite': CreateMode.CREATE_AND_REPLACE,
                    'read': CreateMode.NONE,
                    'delete': CreateMode.NONE,
                    'update': CreateMode.NONE,
                }
                #  Connect to an existing .hyper file
                with Connection(endpoint=hyper_process.endpoint,
                                database=in_dict['hyper file'],
                                create_mode=hyper_create_mode.get(in_dict['action'])
                                ) as hyper_connection:
                    in_logger.debug(self.locale.gettext(
                        'Connection to the Hyper engine using file name "{file_name}" '
                        + 'has been established')
                                    .replace('{file_name}', in_dict['hyper file']))
                    timer.stop()
                    in_dict['connection'] = hyper_connection
                    if in_dict['action'] == 'read':
                        out_data_frame = self.fn_hyper_read(in_logger, timer, in_dict)
                    elif in_dict['action'] in ('append', 'overwrite'):
                        self.fn_write_data_into_hyper_file(in_logger, timer, in_dict)
                    elif in_dict['action'] in ('delete', 'update'):
                        self.fn_delete_data_from_hyper(in_logger, timer, in_dict)
                        self.fn_get_records_count_from_table(in_logger, timer, in_dict)
            timer.start()
            hyper_connection.close()
            in_logger.info(self.locale.gettext(
                'Connection to the Hyper engine file has been closed'))
            in_logger.info(self.locale.gettext('Hyper engine process has been shut down'))
            timer.stop()
        except HyperException as ex:
            in_logger.error(str(ex).replace(chr(10), ' '))
            timer.stop()
            exit(1)
        return out_data_frame

    def fn_hyper_read(self, in_logger, timer, in_dict):
        timer.start()
        # once Hyper is opened we can get data out
        query_to_run = f"SELECT * FROM {TableName('Extract', 'Extract')}"
        in_logger.debug(self.locale.gettext(
            'Hyper SQL about to be executed is: {hyper_sql}')
                        .replace('{hyper_sql}', str(query_to_run)))
        result_set = in_dict['connection'].execute_list_query(query=query_to_run)
        out_data_frame = pd.DataFrame(result_set)
        in_logger.debug(self.locale.gettext(
            'Hyper SQL executed with success and {rows_counted} have been retrieved')
                        .replace('{rows_counted}', str(len(out_data_frame))))
        table_definition = in_dict['connection'].catalog.get_table_definition(
            name=TableName('Extract', 'Extract'))
        table_columns = self.fn_get_column_names_from_table(in_logger, {
            'table definition': table_definition,
        })
        out_data_frame.set_axis(table_columns, axis='columns', inplace=True)
        timer.stop()
        return out_data_frame

    def fn_rebuild_data_frame_content_for_hyper(self, in_logger, timer, in_dict):
        timer.start()
        in_dict['data frame'].replace(to_replace=[numpy.nan], value=[None], inplace=True)
        in_logger.info(self.locale.gettext('Filling empty values with NAN finished'))
        timer.stop()
        timer.start()
        # Cycle through all found columns
        for current_field in in_dict['data frame structure']:
            in_logger.debug(self.locale.gettext(
                'Column {column_name} has pandas data type = {column_pandas_type} '
                + 'and python data type = {column_python_type}')
                            .replace('{column_name}', current_field['name'])
                            .replace('{column_pandas_type}', str(current_field['panda_type']))
                            .replace('{column_python_type}', str(current_field['type'])))
            in_dict['data frame'][current_field['name']] = self.fn_reevaluate_single_column(
                in_dict['data frame'][current_field['name']], current_field)
        timer.stop()
        for converting_data_type in self.hyper_conversion_dtypes:
            in_dict['data frame'] = self.fn_convert_multiple_columns(
                in_logger, timer, in_dict['data frame'], converting_data_type)
        timer.start()
        in_logger.info(self.locale.gettext(
            'Re-building CSV content for maximum Hyper compatibility has been completed'))
        in_logger.info(self.locale.gettext(
            '{rows_counted} records were prepared in this process')
                       .replace('{rows_counted}', str(len(in_dict['data frame']))))
        timer.stop()
        return in_dict['data frame'].values

    def fn_reevaluate_single_column(self, df_column, in_field_details):
        if in_field_details['type'][0:5] in ('date-', 'datet', 'time-'):
            df_column = self.fn_string_to_date(df_column, in_field_details['type'])
        else:
            df_column = self.fn_reevaluate_single_column_additional(df_column, in_field_details)
        return df_column

    def fn_reevaluate_single_column_additional(self, in_df_column, in_field):
        target_data_type = self.fn_standardize_data_type(in_field)
        if target_data_type != '':
            if target_data_type in self.columns_for_hyper_conversion:
                new_index = len(self.columns_for_hyper_conversion[target_data_type])
                self.columns_for_hyper_conversion[target_data_type].append(new_index)
                self.columns_for_hyper_conversion[target_data_type][new_index] = in_field['name']
            else:
                self.columns_for_hyper_conversion[target_data_type] = [in_field['name']]
        return in_df_column

    @staticmethod
    def fn_standardize_data_type(in_field):
        target_data_type = ''
        if in_field['panda_type'] in ('object', 'float64') and in_field['type'] == 'int':
            target_data_type = 'int64'
        elif str(in_field['type']) in ('float-dot', 'str'):
            known_types = {
                'float-dot': 'float',
                'str': 'str',
            }
            target_data_type = known_types.get(in_field['type'])
        return target_data_type

    @staticmethod
    def fn_string_to_date(in_df_column, in_data_type):
        if re.match('-YMD', in_data_type):
            in_df_column = pd.to_datetime(in_df_column, yearfirst=True)
        elif re.match('-DMY', in_data_type):
            in_df_column = pd.to_datetime(in_df_column, dayfirst=True)
        else:
            in_df_column = pd.to_datetime(in_df_column)
        return in_df_column

    def fn_write_data_into_hyper_file(self, in_logger, timer, in_dict):
        if in_dict['action'] == 'append':
            self.fn_get_records_count_from_table(in_logger, timer, {
                'connection': in_dict['connection'],
                'schema name': in_dict['schema name'],
                'table name': in_dict['table name'],
            })
            hyper_table = in_dict['connection'].catalog.get_table_definition(
                TableName('Extract', 'Extract'))
        elif in_dict['action'] == 'overwrite':
            self.fn_create_hyper_schema(in_logger, timer, in_dict)
            hyper_table = self.fn_create_hyper_table(in_logger, timer, {
                'columns': in_dict['hyper table columns'],
                'connection': in_dict['connection'],
                'schema name': in_dict['schema name'],
                'table name': in_dict['table name'],
            })
        self.fn_insert_data_into_hyper_table(in_logger, timer, {
            'connection': in_dict['connection'],
            'data': in_dict['data'],
            'table': hyper_table,
        })
        self.fn_get_records_count_from_table(in_logger, timer, {
            'connection': in_dict['connection'],
            'schema name': in_dict['schema name'],
            'table name': in_dict['table name'],
        })
