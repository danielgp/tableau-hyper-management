import csv

from TypeDetermination import TypeDetermination
from datetime import datetime
from tableauhyperapi import HyperProcess, Telemetry, \
    Connection, CreateMode, \
    NOT_NULLABLE, NULLABLE, SqlType, TableDefinition, \
    Inserter, \
    escape_name, escape_string_literal, \
    TableName, \
    HyperException, \
    Timestamp


class TableauHyperApiExtraLogic:

    def fn_build_hyper_columns_for_csv(given_file_name, csv_field_separator, detected_csv_structure, verbose):
        list_hyper_table_columns_to_return = []
        for current_field_structure in detected_csv_structure:
            list_hyper_table_columns_to_return.append(current_field_structure['order'])
            current_column_type = TableauHyperApiExtraLogic.fn_convert_to_hyper_types(current_field_structure['type'])
            if verbose:
                print('Column ' + str(current_field_structure['order']) + ' having name "'
                      + current_field_structure['name'] + '" and type "'
                      + current_field_structure['type'] + '" will become "'
                      + str(current_column_type) + '"')
            list_hyper_table_columns_to_return[current_field_structure['order']] = TableDefinition.Column(
                name=current_field_structure['name'],
                type=current_column_type,
                nullability=NULLABLE
            )
        return list_hyper_table_columns_to_return

    def fn_convert_to_hyper_types(given_type):
        switcher = {
            'empty': SqlType.text(),
            'int': SqlType.big_int(),
            'float-US': SqlType.double(),
            'date-iso8601': SqlType.date(),
            'time24': SqlType.time(),
            'timeUS': SqlType.time(),
            'datetime-iso8601': SqlType.timestamp(),
            'str': SqlType.text()
        }
        identified_type = switcher.get(given_type)
        if identified_type is None:
            identified_type = SqlType.text()
        return identified_type

    def fn_rebuild_csv_content_for_hyper(given_file_name, csv_field_separator, detected_fields_type, verbose):
        csv_content_for_hyper = []
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
                    if row_content[csv_object.fieldnames[col_idx]] == '':
                        csv_content_for_hyper[row_idx][col_idx] = None
                    else:
                        if detected_fields_type[col_idx]['type'] == 'datetime-iso8601':
                            tm = datetime.fromisoformat(row_content[csv_object.fieldnames[col_idx]])
                            csv_content_for_hyper[row_idx][col_idx] = Timestamp(tm.year, tm.month, tm.day,
                                                                                tm.hour, tm.minute, tm.second)
                        elif detected_fields_type[col_idx]['type'] == 'int':
                            csv_content_for_hyper[row_idx][col_idx] = int(row_content[csv_object.fieldnames[col_idx]])
                        elif detected_fields_type[col_idx]['type'] == 'float-US':
                            csv_content_for_hyper[row_idx][col_idx] = float(row_content[csv_object.fieldnames[col_idx]])
                        else:
                            csv_content_for_hyper[row_idx][col_idx] = row_content[csv_object.fieldnames[col_idx]]. \
                                replace('"', '\\"')
                    if verbose:
                        print(print_prefix + ' column ' + str(col_idx)
                              + ' having the name [' + csv_object.fieldnames[col_idx] + '] '
                              + ' has the value <' + row_content[csv_object.fieldnames[col_idx]]
                              + '> which was interpreted as <<' + str(csv_content_for_hyper[row_idx][col_idx]) + '>>')
        return csv_content_for_hyper

    def fn_run_create_hyper_file_from_csv(input_csv_file,
                                          csv_field_separator,
                                          output_hyper_file,
                                          verbose):
        detected_csv_structure = TypeDetermination.fn_detect_csv_structure(input_csv_file,
                                                                           csv_field_separator,
                                                                           verbose)
        hyper_table_columns = TableauHyperApiExtraLogic.fn_build_hyper_columns_for_csv(input_csv_file,
                                                                                       csv_field_separator,
                                                                                       detected_csv_structure,
                                                                                       verbose)
        # Starts the Hyper Process with telemetry enabled/disabled to send data to Tableau or not
        # To opt in, simply set telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU.
        # To opt out, simply set telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU.
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            # Creates new Hyper file <output_hyper_file>
            # Replaces file with CreateMode.CREATE_AND_REPLACE if it already exists.
            with Connection(endpoint=hyper.endpoint,
                            database=output_hyper_file,
                            create_mode=CreateMode.CREATE_AND_REPLACE) as hyper_connection:
                hyper_connection.catalog.create_schema("Extract")
                hyper_table = TableDefinition(
                    name=TableName("Extract", "Extract"),
                    columns=hyper_table_columns
                )
                hyper_connection.catalog.create_table(table_definition=hyper_table)
                print("The connection to the Hyper engine file has been created.")
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
                data_to_insert = TableauHyperApiExtraLogic.fn_rebuild_csv_content_for_hyper(input_csv_file,
                                                                                            csv_field_separator,
                                                                                            detected_csv_structure,
                                                                                            verbose)
                # Execute the actual insert
                with Inserter(hyper_connection, hyper_table) as hyper_inserter:
                    hyper_inserter.add_rows(rows=data_to_insert)
                    hyper_inserter.execute()
                # Number of rows in the <hyper_table> table.
                # `execute_scalar_query` is for executing a query that returns exactly one row with one column.
                row_count = hyper_connection.\
                    execute_scalar_query(query=f"SELECT COUNT(*) FROM {hyper_table.table_name}")
                print(f"The number of rows in table {hyper_table.table_name} is {row_count}.")
            print("The connection to the Hyper file has been closed.")
        print("The Hyper process has been shut down.")