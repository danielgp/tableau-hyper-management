"""
TableauHyperApiExtraLogic - a Hyper client library.

This library allows packaging CSV content into HYPER format with data type checks
"""

# additional Python packages available from PyPi
import numpy as nmpy
import pandas as pd

# Custom classes from Tableau Hyper package
from tableauhyperapi import HyperProcess, Telemetry, \
    Connection, CreateMode, \
    NOT_NULLABLE, NULLABLE, SqlType, TableDefinition, \
    Inserter, \
    TableName, \
    HyperException


class TableauHyperApiExtraLogic:

    def fn_build_hyper_columns_for_csv(self, logger, detected_csv_structure):
        list_to_return = []
        for current_field_structure in detected_csv_structure:
            list_to_return.append(current_field_structure['order'])
            current_column_type = self.fn_convert_to_hyper_types(current_field_structure['type'])
            logger.debug('Column ' + str(current_field_structure['order']) + ' having name "'
                         + current_field_structure['name'] + '" and type "'
                         + current_field_structure['type'] + '" will become "'
                         + str(current_column_type) + '"')
            nullability_value = NULLABLE
            if current_field_structure['nulls'] == 0:
                nullability_value = NOT_NULLABLE
            list_to_return[current_field_structure['order']] = TableDefinition.Column(
                name=current_field_structure['name'],
                type=current_column_type,
                nullability=nullability_value
            )
        return list_to_return

    @staticmethod
    def fn_convert_to_hyper_types(given_type):
        switcher = {
            'empty'                        : SqlType.text(),
            'bool'                         : SqlType.bool(),
            'int'                          : SqlType.big_int(),
            'float-dot'                    : SqlType.double(),
            'date-iso8601'                 : SqlType.date(),
            'date-DMY-dash'                : SqlType.date(),
            'date-DMY-dot'                 : SqlType.date(),
            'date-DMY-slash'               : SqlType.date(),
            'date-MDY'                     : SqlType.date(),
            'date-MDY-medium'              : SqlType.date(),
            'date-MDY-long'                : SqlType.date(),
            'time-24'                      : SqlType.time(),
            'time-24-micro-sec'            : SqlType.time(),
            'time-12'                      : SqlType.time(),
            'time-12-micro-sec'            : SqlType.time(),
            'datetime-iso8601'             : SqlType.timestamp(),
            'datetime-iso8601-micro-sec'   : SqlType.timestamp(),
            'datetime-MDY'                 : SqlType.timestamp(),
            'datetime-MDY-micro-sec'       : SqlType.timestamp(),
            'datetime-MDY-medium'          : SqlType.timestamp(),
            'datetime-MDY-medium-micro-sec': SqlType.timestamp(),
            'datetime-MDY-long'            : SqlType.timestamp(),
            'datetime-MDY-long-micro-sec'  : SqlType.timestamp(),
            'str'                          : SqlType.text()
        }
        identified_type = switcher.get(given_type)
        if identified_type is None:
            identified_type = SqlType.text()
        return identified_type

    def fn_create_hyper_file_from_csv(self, logger, input_csv_data_frame, in_data_type,
                                      given_parameters):
        hyper_cols = self.fn_build_hyper_columns_for_csv(self, logger, in_data_type)
        # The rows to insert into the <hyper_table> table.
        data_to_insert = self.fn_rebuild_csv_content_for_hyper(logger,
                                                               input_csv_data_frame,
                                                               in_data_type)
        # Starts the Hyper Process with telemetry enabled/disabled to send data to Tableau or not
        # To opt in, simply set telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU.
        # To opt out, simply set telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU.
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            # Creates new Hyper file <output_hyper_file>
            # Replaces file with CreateMode.CREATE_AND_REPLACE if it already exists.
            with Connection(endpoint=hyper.endpoint,
                            database=given_parameters.output_file,
                            create_mode=CreateMode.CREATE_AND_REPLACE) as hyper_connection:
                logger.info('Connection to the Hyper engine '
                            + f'file "{given_parameters.output_file}" has been created.')
                hyper_connection.catalog.create_schema("Extract")
                logger.info('Hyper schema "Extract" has been created.')
                hyper_table = TableDefinition(
                    TableName("Extract", "Extract"),
                    columns=hyper_cols
                )
                hyper_connection.catalog.create_table(table_definition=hyper_table)
                logger.info('Hyper table "Extract" has been created.')
                # Execute the actual insert
                with Inserter(hyper_connection, hyper_table) as hyper_insert:
                    hyper_insert.add_rows(rows=data_to_insert)
                    hyper_insert.execute()
                # Number of rows in the <hyper_table> table.
                # `execute_scalar_query` is for executing a query
                # that returns exactly one row with one column.
                row_count = hyper_connection.\
                    execute_scalar_query(query=f'SELECT COUNT(*) FROM {hyper_table.table_name}')
                logger.info(f'Number of rows in table {hyper_table.table_name} is {row_count}')
            logger.info('Connection to the Hyper engine file has been closed')
        logger.info('Hyper engine process has been shut down')

    @staticmethod
    def fn_rebuild_csv_content_for_hyper(logger, input_df, detected_fields_type):
        input_df.replace(to_replace=[nmpy.nan], value=[None], inplace=True)
        # Cycle through all found columns
        for current_field in detected_fields_type:
            fld_nm = current_field['name']
            logger.debug(f'Column {fld_nm} has panda_type = '
                         + str(current_field['panda_type'])
                         + ' and python type = ' + str(current_field['type']))
            if current_field['panda_type'] == 'float64' and current_field['type'] == 'int':
                input_df[fld_nm] = input_df[fld_nm].fillna(0).astype('int64')
            elif current_field['type'][0:5] in ('date-', 'datet', 'time-'):
                input_df[fld_nm] = pd.to_datetime(input_df[fld_nm])
        return input_df.values

    def fn_run_hyper_creation(self, logger, input_data_frame, input_data_type, given_parameters):
        try:
            self.fn_create_hyper_file_from_csv(self, logger, input_data_frame,
                                               input_data_type, given_parameters)
        except HyperException as ex:
            logger.error(str(ex).replace(chr(10), ' '))
            exit(1)
