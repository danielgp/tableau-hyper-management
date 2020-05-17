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
        hyper_create_mode = {
            'append': CreateMode.NONE,
            'overwrite': CreateMode.CREATE_AND_REPLACE,
            'read': CreateMode.NONE,
            'remove': CreateMode.NONE,
            'update': CreateMode.NONE,
        }
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
                    schema_name = 'Extract'
                    hyper_table_name = 'Extract'
                    if in_dict['action'] == 'read':
                        out_data_frame = self.fn_hyper_read(in_logger, timer, hyper_connection)
                    elif in_dict['action'] in ('append', 'overwrite'):
                        in_dict['connection'] = hyper_connection
                        in_dict['schema name'] = schema_name
                        in_dict['table name'] = hyper_table_name
                        self.fn_write_data_into_hyper_file(in_logger, timer, in_dict)
                    elif in_dict['action'] in ('remove', 'update'):
                        self.fn_remove_data_from_hyper(in_logger, timer, {
                            'connection': hyper_connection,
                            'sql query':
                                in_dict['input parameters'].sql_query_to_remove_or_update_data,
                        })
                        self.fn_get_records_count_from_table(in_logger, timer, {
                            'connection': hyper_connection,
                            'schema name': schema_name,
                            'table name': hyper_table_name,
                        })
            in_logger.info(self.locale.gettext(
                'Connection to the Hyper engine file has been closed'))
            in_logger.info(self.locale.gettext('Hyper engine process has been shut down'))
        except HyperException as ex:
            in_logger.error(str(ex).replace(chr(10), ' '))
            timer.stop()
            exit(1)
        return out_data_frame

    def fn_hyper_read(self, in_logger, timer, in_connection):
        timer.start()
        # once Hyper is opened we can get data out
        query_to_run = f"SELECT * FROM {TableName('Extract', 'Extract')}"
        in_logger.debug(self.locale.gettext(
            'Hyper SQL about to be executed is: {hyper_sql}')
                        .replace('{hyper_sql}', str(query_to_run)))
        result_set = in_connection.execute_list_query(query=query_to_run)
        out_data_frame = pd.DataFrame(result_set)
        in_logger.debug(self.locale.gettext(
            'Hyper SQL executed with success and {rows_counted} have been retrieved')
                        .replace('{rows_counted}', str(len(out_data_frame))))
        table_definition = in_connection.catalog.get_table_definition(
            name=TableName('Extract', 'Extract'))
        table_columns = self.fn_get_column_names_from_table(in_logger, {
            'table definition': table_definition,
        })
        out_data_frame.set_axis(table_columns, axis='columns', inplace=True)
        timer.stop()
        return out_data_frame

    def fn_rebuild_data_frame_content_for_hyper(self, in_logger, timer, in_dict):
        timer.start()
        input_df = in_dict['data frame']
        input_df.replace(to_replace=[numpy.nan], value=[None], inplace=True)
        # Cycle through all found columns
        for current_field in in_dict['data frame structure']:
            fld_nm = current_field['name']
            in_logger.debug(self.locale.gettext(
                'Column {column_name} has pandas data type = {column_pandas_type} '
                + 'and python data type = {column_python_type}')
                            .replace('{column_name}', current_field['name'])
                            .replace('{column_pandas_type}', str(current_field['panda_type']))
                            .replace('{column_python_type}', str(current_field['type'])))
            input_df[fld_nm] = self.fn_reevaluate_single_column(input_df, fld_nm, current_field)
            if current_field['panda_type'] in ('object', 'float64') \
                    and current_field['type'] == 'int':
                input_df[fld_nm] = input_df[fld_nm].fillna(0).astype('int64')
                in_logger.debug(self.locale.gettext(
                    'Column {column_name} has been forced converted to {forced_type}')
                                .replace('{column_name}', current_field['name'])
                                .replace('{forced_type}', 'Int'))
            if str(current_field['type']) == 'float-dot':
                input_df[fld_nm] = input_df[fld_nm].astype(float)
                in_logger.debug(self.locale.gettext(
                    'Column {column_name} has been forced converted to {forced_type}')
                                .replace('{column_name}', current_field['name'])
                                .replace('{forced_type}', 'Float'))
        in_logger.info(self.locale.gettext(
            'Re-building CSV content for maximum Hyper compatibility has been completed'))
        timer.stop()
        return input_df.values

    def fn_reevaluate_single_column(self, given_df, given_field_name, current_field_details):
        if current_field_details['type'] == 'str':
            given_df[given_field_name] = given_df[given_field_name].astype(str)
        elif current_field_details['type'][0:5] in ('date-', 'datet', 'time-'):
            given_df[given_field_name] = self.fn_string_to_date(given_field_name, given_df)
        return given_df[given_field_name]

    def fn_remove_data_from_hyper(self, in_logger, timer, in_dict):
        timer.start()
        in_logger.debug(self.locale.gettext(
            'Hyper SQL about to be executed is: {hyper_sql}')
                        .replace('{hyper_sql}', in_dict['sql query']))
        row_count = in_dict['connection'].execute_command(command=in_dict['sql query'])
        in_logger.debug(self.locale.gettext(
            'Hyper SQL executed with success and {rows_counted} have been retrieved')
                        .replace('{rows_counted}', str(row_count)))
        timer.stop()

    @staticmethod
    def fn_string_to_date(in_col_name, in_data_frame):
        if re.match('-YMD', in_col_name):
            in_data_frame[in_col_name] = pd.to_datetime(in_data_frame[in_col_name], yearfirst=True)
        elif re.match('-DMY', in_col_name):
            in_data_frame[in_col_name] = pd.to_datetime(in_data_frame[in_col_name], dayfirst=True)
        else:
            in_data_frame[in_col_name] = pd.to_datetime(in_data_frame[in_col_name])
        return in_data_frame[in_col_name]

    def fn_write_data_into_hyper_file(self, in_logger, timer, in_dict):
        if in_dict['action'] == 'append':
            self.fn_get_records_count_from_table(in_logger, timer, {
                'connection': in_dict['connection'],
                'schema name': in_dict['schema name'],
                'table name': in_dict['table name'],
            })
            hyper_table = in_dict['connection'].catalog.get_table_names(in_dict['schema name'])[0]
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
