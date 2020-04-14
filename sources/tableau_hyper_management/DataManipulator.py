"""
Data Manipulation class
"""
# package to facilitate operating system operations
import os
# package to facilitate os path manipulations
import pathlib
# package facilitating Data Frames manipulation
import pandas as pd
# package regular expressions
import re


class DataManipulator:

    def fn_apply_query_to_data_frame(self, local_logger, timmer, data_frame, extract_params):
        timmer.start()
        query_expression = ''
        if extract_params['filter_to_apply'] == 'equal':
            local_logger.debug('Will retain only values equal with "'
                               + extract_params['filter_values'] + '" within the field "'
                               + extract_params['column_to_filter'] + '"')
            query_expression = '`' + extract_params['column_to_filter'] + '` == "' \
                               + extract_params['filter_values'] + '"'
        elif extract_params['filter_to_apply'] == 'different':
            local_logger.debug('Will retain only values different than "'
                               + extract_params['filter_values'] + '" within the field "'
                               + extract_params['column_to_filter'] + '"')
            query_expression = '`' + extract_params['column_to_filter'] + '` != "' \
                               + extract_params['filter_values'] + '"'
        elif extract_params['filter_to_apply'] == 'multiple_match':
            local_logger.debug('Will retain only values equal with "'
                               + extract_params['filter_values'] + '" within the field "'
                               + extract_params['column_to_filter'] + '"')
            query_expression = '`' + extract_params['column_to_filter'] + '` in ["' \
                               + '", "'.join(extract_params['filter_values'].values()) \
                               + '"]'
        local_logger.debug('Query expression to apply is: ' + query_expression)
        data_frame.query(query_expression, inplace = True)
        timmer.stop()
        return data_frame

    def build_file_list(self, local_logger, timmer, given_input_file):
        relevant_files_list = []
        if re.search(r'(\*|\?)*', given_input_file):
            local_logger.debug('Files pattern has been provided')
            parent_directory = os.path.dirname(given_input_file)
            # loading from a specific folder all files matching a given pattern into a file list
            relevant_files_list = self.fn_build_relevant_file_list(local_logger, timmer,
                                                                   parent_directory,
                                                                   given_input_file)
        else:
            local_logger.debug('Specific file has been provided')
            relevant_files_list = [given_input_file]
        return relevant_files_list

    @staticmethod
    def fn_build_relevant_file_list(local_logger, timmer, in_folder, matching_pattern):
        timmer.start()
        local_logger.info('Will list all files within ' + in_folder
                          + ' folder looking for ' + matching_pattern + ' as matching pattern')
        list_files = []
        file_counter = 0
        if os.path.isdir(in_folder):
            working_path = pathlib.Path(in_folder)
            for current_file in working_path.iterdir():
                if current_file.is_file() and current_file.match(matching_pattern):
                    list_files.append(file_counter)
                    list_files[file_counter] = str(current_file.absolute())
                    file_counter = file_counter + 1
        local_logger.info('Relevant CSV files from ' + in_folder + ' folder were identified!')
        local_logger.info(list_files)
        timmer.stop()
        return list_files

    def fn_drop_certain_columns(self, local_logger, timmer, working_dictionary):
        for current_file in working_dictionary['files']:
            # load all relevant files into a single data frame
            df = self.fn_load_file_list_to_data_frame(local_logger, timmer, [current_file],
                                                      working_dictionary['csv_field_separator'])
            save_necessary = False
            for column_to_eliminate in working_dictionary['columns_to_eliminate']:
                if column_to_eliminate in df:
                    df.drop(columns = column_to_eliminate, inplace = True)
                    save_necessary = True
            if save_necessary:
                self.fn_store_data_frame_to_file(local_logger, timmer, df, current_file,
                                                 working_dictionary['csv_field_separator'])

    def fn_load_file_list_to_data_frame(self, local_logger, timmer, file_list, csv_delimiter):
        timmer.start()
        combined_csv = pd.concat([pd.read_csv(filepath_or_buffer = current_file,
                                              delimiter = csv_delimiter,
                                              cache_dates = True,
                                              index_col = None,
                                              memory_map = True,
                                              low_memory = False,
                                              encoding = 'utf-8',
                                              ) for current_file in file_list])
        local_logger.info('All relevant files were merged into a Pandas Data Frame')
        timmer.stop()
        return combined_csv

    @staticmethod
    def fn_move_files(local_logger, timmer, source_folder, file_names, destination_folder):
        timmer.start()
        resulted_files = []
        for current_file in file_names:
            new_file_name = current_file.replace(source_folder, destination_folder)
            if new_file_name.is_file():
                os.replace(current_file, new_file_name)
                local_logger.info('File ' + current_file
                                  + ' has just been been overwritten  as ' + new_file_name)
            else:
                os.rename(current_file, new_file_name)
                local_logger.info('File ' + current_file
                                  + ' has just been renamed as ' + new_file_name)
            resulted_files.append(new_file_name)
        timmer.stop()
        return resulted_files

    @staticmethod
    def fn_store_data_frame_to_file(local_logger, timmer, input_data_frame,
                                    destination_file_name, csv_delimiter):
        timmer.start()
        input_data_frame.to_csv(path_or_buf = destination_file_name,
                                sep = csv_delimiter,
                                header = True,
                                index = False,
                                encoding = 'utf-8')
        local_logger.info('Data frame has just been saved to file "' + destination_file_name + '"')
        timmer.stop()
