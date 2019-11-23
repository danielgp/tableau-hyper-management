import os
import pandas as pd
import sys

from BasicNeeds import BasicNeeds as cls_bn
from TypeDetermination import TypeDetermination
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
            cls_bn.fn_optional_print(cls_bn, verbose, 'Column '
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

    def fn_create_hyper_file_from_csv(self, input_csv_file, csv_field_separator, output_hyper_file, verbose):
        detected_csv_structure = TypeDetermination.fn_detect_csv_structure(TypeDetermination,
                                                                           input_csv_file,
                                                                           csv_field_separator,
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
                    name = TableName(schema_name = "Extract", table_name = "Extract"),
                    columns = hyper_table_columns
                )
                hyper_connection.catalog.create_table(table_definition = hyper_table)
                print("Hyper table Extract has been created.")
                '''
                VERDICT: does not work as DOUBLE or INT are not accepting empty values... :-(
                print("I am about to execute command: " 
                    + f"COPY {hyper_table.table_name} from {escape_string_literal(input_csv_file)} with "
                    f"(format csv, NULL 'NULL', delimiter '{csv_field_separator}', header)")
                # Load all rows into "Customers" table from the CSV file.
                # `execute_command` executes a SQL statement and returns the impacted row count.
                count_in_target_table = hyper_connection.execute_command(
                    command=f"COPY {hyper_table.table_name} from {escape_string_literal(input_csv_file)} with "
                    f"(format csv, NULL 'NULL', delimiter '{csv_field_separator}', header)")
                print(f"The number of rows in table {hyper_table.table_name} is {count_in_target_table}.")
                '''
                # The rows to insert into the <hyper_table> table.
                data_to_insert = self.fn_rebuild_csv_content_for_hyper(self,
                                                                       input_csv_file,
                                                                       csv_field_separator,
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

    def fn_rebuild_csv_content_for_hyper(self, given_file_name, csv_field_separator, detected_fields_type, verbose):
        csv_content_for_hyper = []
        # Import the data
        csv_content_df = pd.read_csv(filepath_or_buffer=given_file_name,
                                     delimiter = csv_field_separator,
                                     cache_dates = True,
                                     #keep_default_na = False,
                                     usecols = ['Cost Type', 'Domain'],
                                     encoding = 'utf-8')
        print(csv_content_df)
        csv_content_df.replace(to_replace = [pd.np.nan], value = [None], inplace = True)
        #csv_content_df.replace(to_replace = [""], value = [None], inplace = True)
        #csv_content_df.where(csv_content_df.values == '', [None])
        csv_content_for_hyper = csv_content_df
        print(csv_content_for_hyper)
        '''
        with open(given_file_name, newline='') as csv_file:
            csv_object = csv.DictReader(csv_file, delimiter=csv_field_separator)
            # parse rows with index
            for row_idx, row_content in enumerate(csv_object):
                csv_content_for_hyper.append(row_idx)
                csv_content_for_hyper[row_idx] = []
                print_prefix = 'On the row ' + str((row_idx + 1))
                # parse all columns with index
                for col_idx, column_name in enumerate(csv_object.fieldnames):
                    csv_content_for_hyper[row_idx].append(col_idx)
                    csv_content_for_hyper[row_idx][col_idx] = \
                        self.fn_convert_and_validate_content(row_content[csv_object.fieldnames[col_idx]],
                                                             detected_fields_type[col_idx]['type'])
                    cls_bn.fn_optional_print(cls_bn, verbose, print_prefix + ' column ' + str(col_idx)
                                             + ' having the name [' + csv_object.fieldnames[col_idx] + '] '
                                             + ' has the value <' + row_content[csv_object.fieldnames[col_idx]]
                                             + '> which was interpreted as <<'
                                             + str(csv_content_for_hyper[row_idx][col_idx])
                                             + '>>')
        '''
        return csv_content_for_hyper

    def fn_run_hyper_creation(self, input_csv_file, csv_field_separator, output_hyper_file, verbose):
        try:
            self.fn_create_hyper_file_from_csv(self, input_csv_file, csv_field_separator, output_hyper_file, verbose)
        except HyperException as ex:
            print(ex)
            exit(1)
