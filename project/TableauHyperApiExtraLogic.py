import pandas as pd

from BasicNeeds import BasicNeeds as _cls_bn
from TypeDetermination import TypeDetermination as _cls_td

from datetime import datetime,time
from tableauhyperapi import HyperProcess, Telemetry, \
    Connection, CreateMode, \
    NOT_NULLABLE, NULLABLE, SqlType, TableDefinition, \
    Inserter, \
    escape_name, escape_string_literal, \
    TableName, \
    HyperException, \
    Timestamp


class TableauHyperApiExtraLogic:

    def fn_build_hyper_columns_for_csv(self, detected_csv_structure, verbose):
        list_hyper_table_columns_to_return = []
        for current_field_structure in detected_csv_structure:
            list_hyper_table_columns_to_return.append(current_field_structure['order'])
            current_column_type = self.fn_convert_to_hyper_types(current_field_structure['type'])
            _cls_bn.fn_optional_print(_cls_bn, verbose, 'Column '
                                      + str(current_field_structure['order']) + ' having name "'
                                      + current_field_structure['name'] + '" and type "'
                                      + current_field_structure['type'] + '" will become "'
                                      + str(current_column_type) + '"')
            if current_field_structure['nulls'] == 0:
                list_hyper_table_columns_to_return[current_field_structure['order']] = TableDefinition.Column(
                    name = current_field_structure['name'],
                    type = current_column_type,
                    nullability = NOT_NULLABLE
                )
            else:
                list_hyper_table_columns_to_return[current_field_structure['order']] = TableDefinition.Column(
                    name = current_field_structure['name'],
                    type = current_column_type,
                    nullability = NULLABLE
                )
        return list_hyper_table_columns_to_return
    
    '''
    def fn_convert_and_validate_content(crt_value, crt_type):
        if crt_value == '':
            return None
        else:
            if crt_type == 'int':
                return int(crt_value)
            elif crt_type == 'float-USA':
                return float(crt_value)
            elif crt_type == 'date-iso8601':
                tm = datetime.strptime(crt_value, '%Y-%m-%d')
                return datetime(tm.year, tm.month, tm.day)
            elif crt_type == 'date-USA':
                tm = datetime.strptime(crt_value, '%m/%d/%Y')
                return datetime(tm.year, tm.month, tm.day)
            elif crt_type == 'time-24':
                tm = datetime.strptime(crt_value, '%H:%M:%S')
                return time(tm.hour, tm.minute, tm.second)
            elif crt_type == 'time-24-us':
                tm = datetime.strptime(crt_value, '%H:%M:%S.%f')
                return time(tm.hour, tm.minute, tm.second, tm.microsecond)
            elif crt_type == 'time-USA':
                tm = datetime.strptime(crt_value, '%I:%M:%S')
                return time(tm.hour, tm.minute, tm.second)
            elif crt_type == 'datetime-iso8601':
                tm = datetime.fromisoformat(crt_value)
                return Timestamp(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second)
            elif crt_type == 'datetime-iso8601-us':
                tm = datetime.fromisoformat(crt_value)
                return Timestamp(tm.year, tm.month, tm.day, tm.hour, tm.minute, tm.second, tm.microsecond)
            else:
                return crt_value.replace('"', '\\"')
    '''

    @staticmethod
    def fn_convert_to_hyper_types(given_type):
        switcher = {
            'empty': SqlType.text(),
            'int': SqlType.big_int(),
            'float-USA': SqlType.double(),
            'date-iso8601': SqlType.date(),
            'date-USA': SqlType.date(),
            'time-24': SqlType.time(),
            'time-24-us': SqlType.time(),
            'time-USA': SqlType.time(),
            'datetime-iso8601': SqlType.timestamp(),
            'str': SqlType.text()
        }
        identified_type = switcher.get(given_type)
        if identified_type is None:
            identified_type = SqlType.text()
        return identified_type

    def fn_create_hyper_file_from_csv(self, input_csv_data_frame, output_hyper_file, verbose):
        detected_csv_structure = _cls_td.fn_detect_csv_structure(_cls_td,
                                                                 input_csv_data_frame,
                                                                 verbose)
        hyper_table_columns = self.fn_build_hyper_columns_for_csv(self, detected_csv_structure, verbose)
        # Starts the Hyper Process with telemetry enabled/disabled to send data to Tableau or not
        # To opt in, simply set telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU.
        # To opt out, simply set telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU.
        with HyperProcess(telemetry = Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            # Creates new Hyper file <output_hyper_file>
            # Replaces file with CreateMode.CREATE_AND_REPLACE if it already exists.
            with Connection(endpoint = hyper.endpoint,
                            database = output_hyper_file,
                            create_mode = CreateMode.CREATE_AND_REPLACE) as hyper_connection:
                print("The connection to the Hyper engine file has been created.")
                hyper_connection.catalog.create_schema("Extract")
                print("Hyper schema Extract has been created.")
                hyper_table = TableDefinition(
                    TableName("Extract", "Extract"),
                    columns = hyper_table_columns
                )
                hyper_connection.catalog.create_table(table_definition = hyper_table)
                print("Hyper table Extract has been created.")
                # The rows to insert into the <hyper_table> table.
                data_to_insert = self.fn_rebuild_csv_content_for_hyper(self,
                                                                       input_csv_data_frame,
                                                                       detected_csv_structure,
                                                                       verbose)
                # Execute the actual insert
                with Inserter(hyper_connection, hyper_table) as hyper_inserter:
                    hyper_inserter.add_rows(rows = data_to_insert)
                    hyper_inserter.execute()
                # Number of rows in the <hyper_table> table.
                # `execute_scalar_query` is for executing a query that returns exactly one row with one column.
                row_count = hyper_connection.\
                    execute_scalar_query(query = f'SELECT COUNT(*) FROM {hyper_table.table_name}')
                print(f'The number of rows in table {hyper_table.table_name} is {row_count}.')
            print('The connection to the Hyper file has been closed.')
        print('The Hyper process has been shut down.')

    def fn_rebuild_csv_content_for_hyper(self, input_csv_data_frame, detected_fields_type, verbose):
        input_csv_data_frame.replace(to_replace = [pd.np.nan], value = [None], inplace = True)
        # Cycle through all found columns
        for current_field in detected_fields_type:
            fld_nm = current_field['name']
            if current_field['panda_type'] == 'float64' and current_field['type'] == 'int':
                #input_csv_data_frame[fld_nm] = input_csv_data_frame[fld_nm].apply(lambda x: None if x is None else round(x, 0))
                input_csv_data_frame[fld_nm] = input_csv_data_frame[fld_nm].replace(to_replace = [pd.np.nan, '.0'],
                                                                                    value = [None, ''],
                                                                                    inplace = True)
            elif current_field['type'] == 'datetime-iso8601':
                input_csv_data_frame[fld_nm] = pd.to_datetime(input_csv_data_frame[fld_nm])
        _cls_bn.fn_optional_print(_cls_bn, verbose, 'Column ' + fld_nm + ' '
                                  + 'has panda_type = ' + str(current_field['panda_type']) + ' '
                                  + 'and ' + str(current_field['type']))
        return input_csv_data_frame.values

    def fn_run_hyper_creation(self, input_csv_data_frame, output_hyper_file, verbose):
        try:
            self.fn_create_hyper_file_from_csv(self, input_csv_data_frame, output_hyper_file, verbose)
        except HyperException as ex:
            print(ex)
            exit(1)
