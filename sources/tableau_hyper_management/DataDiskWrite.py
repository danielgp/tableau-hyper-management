"""
DataInput - class to handle data storing to disk (from Pandas Data Frame
"""


class DataDiskWrite:
    implemented_disk_write_file_types = ['csv', 'excel', 'json', 'parquet', 'pickle']

    @staticmethod
    def fn_internal_store_data_frame_to_csv_file(in_dict):
        if in_dict['format'].lower() == 'csv':
            try:
                in_dict['in data frame'].to_csv(
                    path_or_buf=in_dict['name'], sep=in_dict['field delimiter'],
                    header=True, index=False, encoding='utf-8')
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_store_data_frame_to_excel_file(in_dict):
        if in_dict['format'].lower() == 'excel':
            try:
                in_dict['in data frame'].to_excel(
                    excel_writer=in_dict['name'], engine='xlsxwriter',
                    freeze_panes=(1, 1), encoding='utf-8', index=False, verbose=False)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_store_data_frame_to_json_file(in_dict):
        if in_dict['format'].lower() == 'json':
            try:
                in_dict['in data frame'].to_json(
                    path_or_buf=in_dict['name'], compression=in_dict['compression'])
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_store_data_frame_to_parquet_file(in_dict):
        if in_dict['format'].lower() == 'parquet':
            try:
                in_dict['in data frame'].to_parquet(
                    path=in_dict['name'], compression=in_dict['compression'],
                    use_deprecated_int96_timestamps=True)
            except Exception as err:
                in_dict['error details'] = err
        return in_dict

    @staticmethod
    def fn_internal_store_data_frame_to_pickle_file(in_dict):
        if in_dict['format'].lower() == 'pickle':
            try:
                in_dict['in data frame'].to_pickle(
                    path=in_dict['name'], compression=in_dict['compression'])
            except Exception as err:
                in_dict['error details'] = err
        return in_dict
