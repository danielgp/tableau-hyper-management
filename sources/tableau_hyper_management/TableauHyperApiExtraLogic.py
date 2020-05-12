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
from tableauhyperapi import HyperProcess, Telemetry, \
    Connection, CreateMode, \
    NOT_NULLABLE, NULLABLE, SqlType, TableDefinition, \
    Inserter, \
    TableName, \
    HyperException


class TableauHyperApiExtraLogic:
    locale = None
    supported_input_file_types = ('csv', 'json', 'parquet', 'pickle')

    def __init__(self, in_language):
        file_parts = os.path.normpath(os.path.abspath(__file__)).replace('\\', os.path.altsep)\
            .split(os.path.altsep)
        locale_domain = file_parts[(len(file_parts)-1)].replace('.py', '')
        locale_folder = os.path.normpath(os.path.join(
            os.path.join(os.path.altsep.join(file_parts[:-2]), 'project_locale'), locale_domain))
        self.locale = gettext.translation(locale_domain, localedir=locale_folder,
                                          languages=[in_language], fallback=True)

    def fn_build_hyper_columns_for_csv(self, logger, timer, detected_csv_structure):
        timer.start()
        list_to_return = []
        for current_field_structure in detected_csv_structure:
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

    def fn_create_hyper_file_from_csv(self, local_logger, timer, input_csv_data_frame,
                                      in_data_type, given_parameters):
        hyper_cols = self.fn_build_hyper_columns_for_csv(local_logger, timer, in_data_type)
        # The rows to insert into the <hyper_table> table.
        data_to_insert = self.fn_rebuild_csv_content_for_hyper(
                local_logger, timer, input_csv_data_frame, in_data_type)
        # Starts the Hyper Process with telemetry enabled/disabled to send data to Tableau or not
        # To opt in, simply set telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU.
        # To opt out, simply set telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU.
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            # Creates new Hyper file <output_hyper_file>
            # Replaces file with CreateMode.CREATE_AND_REPLACE if it already exists.
            timer.start()
            with Connection(endpoint=hyper.endpoint,
                            database=given_parameters.output_file,
                            create_mode=CreateMode.CREATE_AND_REPLACE) as hyper_connection:
                local_logger.info('Connection to the Hyper engine '
                                  + f'file "{given_parameters.output_file}" has been created.')
                timer.stop()
                schema_name = 'Extract'
                self.fn_create_hyper_schema(local_logger, timer, hyper_connection, schema_name)
                hyper_table_name = 'Extract'
                hyper_table = self.fn_create_hyper_table(local_logger, timer, {
                    'columns': hyper_cols,
                    'connection': hyper_connection,
                    'schema name': schema_name,
                    'table name': hyper_table_name,
                })
                self.fn_insert_data_into_hyper_table(local_logger, timer, {
                    'connection': hyper_connection,
                    'data': data_to_insert,
                    'table': hyper_table,
                })
                self.fn_get_records_count_from_table(local_logger, timer, {
                    'connection': hyper_connection,
                    'table': hyper_table,
                })
            local_logger.info(self.locale.gettext(
                'Connection to the Hyper engine file has been closed'))
        local_logger.info(self.locale.gettext('Hyper engine process has been shut down'))

    def fn_insert_data_into_hyper_table(self, local_logger, timer, in_dict):
        timer.start()
        # Execute the actual insert
        with Inserter(in_dict['connection'], in_dict['table']) as hyper_insert:
            hyper_insert.add_rows(rows=in_dict['data'])
            hyper_insert.execute()
        local_logger.info(self.locale.gettext('Data has been inserted into Hyper table'))
        timer.stop()

    def fn_create_hyper_schema(self, local_logger, timer, in_hyper_connection, in_schema_name):
        timer.start()
        in_hyper_connection.catalog.create_schema(in_schema_name)
        local_logger.info(self.locale.gettext(
            'Hyper schema "{hyper_schema_name}" has been created')
                          .replace('{hyper_schema_name}', in_schema_name))
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

    def fn_get_records_count_from_table(self, local_logger, timer, in_dict):
        timer.start()
        # Number of rows in the <hyper_table> table.
        # `execute_scalar_query` is for executing a query
        # that returns exactly one row with one column.
        query_to_run = 'SELECT COUNT(*) FROM {hyper_table_name}'\
            .replace('{hyper_table_name}', str(in_dict['table'].table_name))
        row_count = in_dict['connection'].execute_scalar_query(query=query_to_run)
        local_logger.info(self.locale.gettext(
            'Table {hyper_table_name} has {row_count} rows')
                          .replace('{hyper_table_name}', str(in_dict['table'].table_name))
                          .replace('{row_count}', str(row_count)))
        timer.stop()

    def fn_rebuild_csv_content_for_hyper(self, in_logger, timer, input_df, detected_fields_type):
        timer.start()
        input_df.replace(to_replace=[numpy.nan], value=[None], inplace=True)
        # Cycle through all found columns
        for current_field in detected_fields_type:
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

    def fn_run_hyper_creation(self, local_logger, timer, input_data_frame, input_data_type,
                              given_parameters):
        try:
            self.fn_create_hyper_file_from_csv(local_logger, timer, input_data_frame,
                                               input_data_type, given_parameters)
        except HyperException as ex:
            local_logger.error(str(ex).replace(chr(10), ' '))
            exit(1)

    @staticmethod
    def fn_string_to_date(in_col_name, in_data_frame):
        if re.match('-YMD', in_col_name):
            in_data_frame[in_col_name] = pd.to_datetime(in_data_frame[in_col_name], yearfirst=True)
        elif re.match('-DMY', in_col_name):
            in_data_frame[in_col_name] = pd.to_datetime(in_data_frame[in_col_name], dayfirst=True)
        else:
            in_data_frame[in_col_name] = pd.to_datetime(in_data_frame[in_col_name])
        return in_data_frame[in_col_name]
