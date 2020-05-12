"""
DataOutput - class to handle disk file storage
"""
# package facilitating Data Frames manipulation
import pandas


class DataDiskRead:

    @staticmethod
    def fn_internal_load_csv_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'csv':
            try:
                in_dict['out data frame'] = pandas.concat(
                        [pandas.read_csv(filepath_or_buffer = crt_file,
                                         delimiter = in_dict['field delimiter'],
                                         cache_dates = True,
                                         index_col = None,
                                         memory_map = True,
                                         low_memory = False,
                                         encoding = 'utf-8',
                                         ) for crt_file in in_dict['files list']],
                        sort = False)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_excel_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'excel':
            try:
                in_dict['out data frame'] = pandas.concat(
                        [pandas.read_excel(io = crt_file,
                                           verbose = True,
                                           ) for crt_file in in_dict['files list']],
                        sort = False)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_json_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'json':
            try:
                in_dict['out data frame'] = pandas.concat(
                        [pandas.read_json(path_or_buf = crt_file,
                                          compression = in_dict['compression'],
                                          ) for crt_file in in_dict['files list']],
                        sort = False)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_parquet_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'parquet':
            try:
                in_dict['out data frame'] = pandas.concat(
                        [pandas.read_parquet(path = crt_file,
                                             ) for crt_file in in_dict['files list']],
                        sort = False)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_pickle_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'pickle':
            try:
                in_dict['out data frame'] = pandas.concat(
                        [pandas.read_pickle(filepath_or_buffer = crt_file,
                                            compression = in_dict['compression'],
                                            ) for crt_file in in_dict['files list']],
                        sort = False)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict
