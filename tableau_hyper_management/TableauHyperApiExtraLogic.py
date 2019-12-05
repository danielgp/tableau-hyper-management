"""
TableauHyperApiExtraLogic - a Hyper client library.

This library allows packaging CSV content into HYPER format with data type checks
"""

import pandas as pd

from . import BasicNeeds as ClassBN
from . import TypeDetermination as ClassTD

from tableauhyperapi import HyperProcess, Telemetry, \
    Connection, CreateMode, \
    NOT_NULLABLE, NULLABLE, SqlType, TableDefinition, \
    Inserter, \
    TableName, \
    HyperException


class TableauHyperApiExtraLogic:

    def fn_build_hyper_columns_for_csv(self, detected_csv_structure, verbose):
        list_to_return = []
        for current_field_structure in detected_csv_structure:
            list_to_return.append(current_field_structure['order'])
            current_column_type = self.fn_convert_to_hyper_types(current_field_structure['type'])
            ClassBN.fn_optional_print(ClassBN, verbose, 'Column '
                                      + str(current_field_structure['order']) + ' having name "'
                                      + current_field_structure['name'] + '" and type "'
                                      + current_field_structure['type'] + '" will become "'
                                      + str(current_column_type) + '"')
            if current_field_structure['nulls'] == 0:
                list_to_return[current_field_structure['order']] = TableDefinition.Column(
                    name=current_field_structure['name'],
                    type=current_column_type,
                    nullability=NOT_NULLABLE
                )
            else:
                list_to_return[current_field_structure['order']] = TableDefinition.Column(
                    name=current_field_structure['name'],
                    type=current_column_type,
                    nullability=NULLABLE
                )
        return list_to_return

    @staticmethod
    def fn_convert_to_hyper_types(given_type):
        switcher = {
            'empty': SqlType.text(),
            'int': SqlType.big_int(),
            'float-USA': SqlType.double(),
            'date-iso8601': SqlType.date(),
            'date-USA': SqlType.date(),
            'time-24': SqlType.time(),
            'time-24-micro-sec': SqlType.time(),
            'time-USA': SqlType.time(),
            'time-USA-micro-sec': SqlType.time(),
            'datetime-iso8601': SqlType.timestamp(),
            'datetime-iso8601-micro-sec': SqlType.timestamp(),
            'str': SqlType.text()
        }
        identified_type = switcher.get(given_type)
        if identified_type is None:
            identified_type = SqlType.text()
        return identified_type

    def fn_create_hyper_file_from_csv(self, input_csv_data_frame, formats_to_evaluate,
                                      output_hyper_file, verbose):
        detected_csv_structure = ClassTD.fn_detect_csv_structure(ClassTD, input_csv_data_frame,
                                                                 formats_to_evaluate, verbose)
        hyper_cols = self.fn_build_hyper_columns_for_csv(self, detected_csv_structure, verbose)
        # Starts the Hyper Process with telemetry enabled/disabled to send data to Tableau or not
        # To opt in, simply set telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU.
        # To opt out, simply set telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU.
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            # Creates new Hyper file <output_hyper_file>
            # Replaces file with CreateMode.CREATE_AND_REPLACE if it already exists.
            with Connection(endpoint=hyper.endpoint,
                            database=output_hyper_file,
                            create_mode=CreateMode.CREATE_AND_REPLACE) as hyper_connection:
                print(f'Connection to the Hyper engine file "{output_hyper_file}" '
                      + 'has been created.')
                hyper_connection.catalog.create_schema("Extract")
                print('Hyper schema "Extract" has been created.')
                hyper_table = TableDefinition(
                    TableName("Extract", "Extract"),
                    columns=hyper_cols
                )
                hyper_connection.catalog.create_table(table_definition=hyper_table)
                print('Hyper table "Extract" has been created.')
                # The rows to insert into the <hyper_table> table.
                data_to_insert = self.fn_rebuild_csv_content_for_hyper(self, input_csv_data_frame,
                                                                       detected_csv_structure,
                                                                       verbose)
                # Execute the actual insert
                with Inserter(hyper_connection, hyper_table) as hyper_inserter:
                    hyper_inserter.add_rows(rows=data_to_insert)
                    hyper_inserter.execute()
                # Number of rows in the <hyper_table> table.
                # `execute_scalar_query` is for executing a query
                # that returns exactly one row with one column.
                row_count = hyper_connection.\
                    execute_scalar_query(query=f'SELECT COUNT(*) FROM {hyper_table.table_name}')
                print(f'Number of rows in table {hyper_table.table_name} is {row_count}.')
            print('Connection to the Hyper engine file has been closed.')
        print('Hyper engine process has been shut down.')

    def fn_rebuild_csv_content_for_hyper(self, input_df, detected_fields_type, verbose):
        input_df.replace(to_replace=[pd.np.nan], value=[None], inplace=True)
        # Cycle through all found columns
        for current_field in detected_fields_type:
            fld_nm = current_field['name']
            ClassBN.fn_optional_print(ClassBN, verbose, 'Column ' + fld_nm
                                      + ' has panda_type = ' + str(current_field['panda_type'])
                                      + ' and ' + str(current_field['type']))
            if current_field['panda_type'] == 'float64' and current_field['type'] == 'int':
                input_df[fld_nm] = input_df[fld_nm].replace(to_replace=[pd.np.nan, '.0'],
                                                            value=[None, ''],
                                                            inplace=True)
            elif current_field['type'] in ('datetime-iso8601', 'datetime-iso8601-micro-sec'):
                input_df[fld_nm] = pd.to_datetime(input_df[fld_nm])
        return input_df.values

    def fn_run_hyper_creation(self, input_data_frame, data_type_and_their_formats_to_evaluate,
                              output_hyper_file, verbose):
        try:
            self.fn_create_hyper_file_from_csv(self, input_data_frame,
                                               data_type_and_their_formats_to_evaluate,
                                               output_hyper_file,
                                               verbose)
        except HyperException as ex:
            print(ex)
            exit(1)
