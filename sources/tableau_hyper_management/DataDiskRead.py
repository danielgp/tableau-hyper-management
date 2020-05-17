"""
DataOutput - class to handle disk file storage
"""
# package to handle files/folders and related metadata/operations
import os
# package facilitating Data Frames manipulation
import pandas


class DataDiskRead:

    @staticmethod
    def fn_internal_load_csv_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'csv':
            try:
                out_data_frame = []
                for index_file, crt_file in enumerate(in_dict['files list']):
                    out_data_frame.append(index_file)
                    out_data_frame[index_file] = pandas.read_csv(
                        filepath_or_buffer=crt_file, delimiter=in_dict['field delimiter'],
                        cache_dates=True, index_col=None, memory_map=True, low_memory=False,
                        encoding='utf-8')
                    out_data_frame[index_file]['Source Data File Name'] = os.path.basename(crt_file)
                in_dict['out data frame'] = pandas.concat(out_data_frame)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_excel_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'excel':
            try:
                out_data_frame = []
                for index_file, crt_file in enumerate(in_dict['files list']):
                    out_data_frame.append(index_file)
                    out_data_frame[index_file] = pandas.read_excel(io=crt_file, verbose=True)
                    out_data_frame[index_file]['Source Data File Name'] = os.path.basename(crt_file)
                in_dict['out data frame'] = pandas.concat(out_data_frame)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_json_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'json':
            try:
                out_data_frame = []
                for index_file, crt_file in enumerate(in_dict['files list']):
                    out_data_frame.append(index_file)
                    out_data_frame[index_file] = pandas.read_json(
                        path_or_buf=crt_file, compression=in_dict['compression'])
                    out_data_frame[index_file]['Source Data File Name'] = os.path.basename(crt_file)
                in_dict['out data frame'] = pandas.concat(out_data_frame)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_parquet_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'parquet':
            try:
                out_data_frame = []
                for index_file, crt_file in enumerate(in_dict['files list']):
                    out_data_frame.append(index_file)
                    out_data_frame[index_file] = pandas.read_parquet(path=crt_file)
                    out_data_frame[index_file]['Source Data File Name'] = os.path.basename(crt_file)
                in_dict['out data frame'] = pandas.concat(out_data_frame)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_load_pickle_file_into_data_frame(in_dict):
        if in_dict['format'].lower() == 'pickle':
            try:
                out_data_frame = []
                for index_file, crt_file in enumerate(in_dict['files list']):
                    out_data_frame.append(index_file)
                    out_data_frame[index_file] = pandas.read_pickle(
                        filepath_or_buffer=crt_file, compression=in_dict['compression'])
                    out_data_frame[index_file]['Source Data File Name'] = os.path.basename(crt_file)
                in_dict['out data frame'] = pandas.concat(out_data_frame)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict
