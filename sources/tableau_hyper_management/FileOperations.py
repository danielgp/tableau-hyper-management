"""
facilitates File Operations
"""
# package to handle date and times
from datetime import datetime
# package to add support for multi-language (i18n)
import gettext
# package to get ability to search file recursively
import glob
# package to use for checksum calculations (in this file)
import hashlib
# package to handle json files
import json
# package to facilitate operating system operations
import os
# package to facilitate os path manipulations
import pathlib
# package regular expressions
import re


class FileOperations:
    timestamp_format = '%Y-%m-%d %H:%M:%S.%f %Z'
    locale = None

    def __init__(self, in_language='en_US'):
        file_parts = os.path.normpath(os.path.abspath(__file__)).replace('\\', os.path.altsep)\
            .split(os.path.altsep)
        locale_domain = file_parts[(len(file_parts)-1)].replace('.py', '')
        locale_folder = os.path.normpath(os.path.join(
            os.path.join(os.path.altsep.join(file_parts[:-2]), 'project_locale'), locale_domain))
        self.locale = gettext.translation(locale_domain, localedir=locale_folder,
                                          languages=[in_language], fallback=True)

    def fn_build_file_list(self, local_logger, timer, given_input_file):
        timer.start()
        if re.search(r'(\*|\?)*', given_input_file):
            local_logger.debug(self.locale.gettext('File matching pattern identified'))
            parent_directory = os.path.dirname(given_input_file)
            # loading from a specific folder all files matching a given pattern into a file list
            relevant_files_list = self.fn_build_relevant_file_list(
                local_logger, parent_directory, given_input_file)
        else:
            local_logger.debug(self.locale.gettext('Specific file name provided'))
            relevant_files_list = [given_input_file]
        timer.stop()
        return relevant_files_list

    def fn_build_relevant_file_list(self, local_logger, in_folder, matching_pattern):
        folder_parts = pathlib.Path(matching_pattern).parts
        search_pattern = folder_parts[(len(folder_parts)-1)]
        local_logger.info(
            self.locale.gettext('Listing all files within {in_folder} folder '
                                + 'looking for {matching_pattern} as matching pattern')
                    .replace('{in_folder}', in_folder)
                    .replace('{matching_pattern}', search_pattern))
        list_files = []
        if os.path.isdir(in_folder):
            list_files = glob.glob(matching_pattern)
            file_counter = len(list_files)
            local_logger.info(self.locale.ngettext(
                '{files_counted} file from {in_folder} folder identified',
                '{files_counted} files from {in_folder} folder identified', file_counter)
                              .replace('{files_counted}', str(file_counter))
                              .replace('{in_folder}', in_folder))
        else:
            local_logger.error(self.locale.gettext('Folder {folder_name} does not exist')
                               .replace('{folder_name}', in_folder))
        return list_files

    def fn_get_file_content(self, in_file_handler, in_file_type):
        if in_file_type == 'json':
            try:
                json_interpreted_details = json.load(in_file_handler)
                print(datetime.utcnow().strftime(self.timestamp_format) + '- ' +
                      self.locale.gettext('JSON structure interpreted'))
                return json_interpreted_details
            except Exception as e:
                print(datetime.utcnow().strftime(self.timestamp_format) + '- ' +
                      self.locale.gettext('Error encountered when trying to interpret JSON'))
                print(e)
        elif in_file_type == 'raw':
            raw_interpreted_file = in_file_handler.read()
            print(datetime.utcnow().strftime(self.timestamp_format) + '- ' +
                  self.locale.gettext('Entire file content read'))
            return raw_interpreted_file
        else:
            print(datetime.utcnow().strftime(self.timestamp_format) + '- ' +
                  self.locale.gettext('Unknown file type provided, '
                                      + 'expected either "json" or "raw" but got {in_file_type}')
                  .replace('{in_file_type}', in_file_type))

    @staticmethod
    def fn_get_file_dates_raw(file_to_evaluate):
        return {
            'created': os.path.getctime(file_to_evaluate),
            'last modified': os.path.getmtime(file_to_evaluate),
        }

    @staticmethod
    def fn_get_file_dates(file_to_evaluate):
        return {
            'created': datetime.fromtimestamp(os.path.getctime(file_to_evaluate)),
            'last modified': datetime.fromtimestamp(os.path.getmtime(file_to_evaluate)),
        }

    def fn_get_file_simple_statistics(self, file_to_evaluate):
        file_date_time = self.fn_get_file_dates(file_to_evaluate)
        return {
            'date when created': datetime.strftime(file_date_time['created'],
                                                   self.timestamp_format).strip(),
            'date when last modified': datetime.strftime(file_date_time['last modified'],
                                                         self.timestamp_format).strip(),
            'size [bytes]': os.path.getsize(file_to_evaluate),
        }

    def fn_get_file_statistics(self, in_dict):
        file_statistics = self.fn_get_file_simple_statistics(in_dict['file name'])
        if in_dict['checksum included'] == 'Yes':
            try:
                file_handler = open(file=in_dict['file name'], mode='r', encoding='mbcs')
            except UnicodeDecodeError:
                file_handler = open(file=in_dict['file name'], mode='r', encoding='utf-8')
            file_content = file_handler.read().encode('utf-8', 'xmlcharrefreplace')
            file_handler.close()
            file_statistics['MD5 Checksum'] = hashlib.md5(file_content).hexdigest()
            file_statistics['SHA1 Checksum'] = hashlib.sha1(file_content).hexdigest()
            file_statistics['SHA224 Checksum'] = hashlib.sha224(file_content).hexdigest()
            file_statistics['SHA256 Checksum'] = hashlib.sha256(file_content).hexdigest()
            file_statistics['SHA384 Checksum'] = hashlib.sha384(file_content).hexdigest()
            file_statistics['SHA512 Checksum'] = hashlib.sha512(file_content).hexdigest()
        return file_statistics

    def fn_get_file_datetime_verdict(self, local_logger, file_to_evaluate,
                                     created_or_modified, reference_datetime):
        implemented_choices = ['created', 'last modified']
        verdict = self.locale.gettext('unknown')
        file_date_time = self.fn_get_file_dates_raw(file_to_evaluate)
        if created_or_modified in implemented_choices:
            which_datetime = file_date_time.get(created_or_modified)
            verdict = self.locale.gettext('older')
            if which_datetime > reference_datetime:
                verdict = self.locale.gettext('newer')
            elif which_datetime == reference_datetime:
                verdict = self.locale.gettext('same')
            str_file_datetime = datetime.strftime(
                datetime.fromtimestamp(which_datetime), self.timestamp_format).strip()
            str_reference = datetime.strftime(
                datetime.fromtimestamp(reference_datetime), self.timestamp_format).strip()
            local_logger.debug(self.locale.gettext(
                    'File "{file_name}" which has the {created_or_modified} datetime '
                    + 'as "{file_datetime}" vs. "{reference_datetime}" '
                    + 'has a verdict = {verdict}')
                              .replace('{file_name}', str(file_to_evaluate))
                              .replace('{created_or_modified}',
                                       self.locale.gettext(created_or_modified))
                              .replace('{reference_datetime}', str_reference)
                              .replace('{file_datetime}', str_file_datetime)
                              .replace('{verdict}', verdict))
        else:
            local_logger.error(self.locale.gettext(
                    'Unknown file datetime choice, '
                    + 'expected is one of the following choices "{implemented_choices}" '
                    + 'but provided was "{created_or_modified}"...')
                               .replace('{implemented_choices}', '", "'.join(implemented_choices))
                               .replace('{created_or_modified}', created_or_modified))
        return verdict

    def fn_move_files(self, local_logger, timer, file_names, destination_folder):
        timer.start()
        resulted_files = []
        for current_file in file_names:
            source_folder = os.path.dirname(current_file)
            new_file_name = current_file.replace(source_folder, destination_folder)
            if os.path.isfile(new_file_name):
                local_logger.warning(self.locale.gettext('File {file_name} will be overwritten')
                                     .replace('{file_name}', current_file))
                os.replace(current_file, new_file_name)
                local_logger.info(self.locale.gettext(
                    'File {file_name} has just been been overwritten as {new_file_name}')
                                     .replace('{file_name}', current_file)
                                     .replace('{new_file_name}', current_file))
            else:
                local_logger.info(self.locale.gettext(
                    'File {file_name} will be renamed as {new_file_name}')
                                     .replace('{file_name}', current_file)
                                     .replace('{new_file_name}', current_file))
                os.rename(current_file, new_file_name)
                local_logger.info(self.locale.gettext(
                    'File {file_name} has just been renamed as {new_file_name}')
                                     .replace('{file_name}', current_file)
                                     .replace('{new_file_name}', current_file))
            resulted_files.append(str(new_file_name))
        timer.stop()
        return resulted_files

    def fn_open_file_and_get_content(self, input_file, content_type='json'):
        if os.path.isfile(input_file):
            with open(input_file, 'r') as file_handler:
                print(datetime.utcnow().strftime(self.timestamp_format) + '- ' +
                      self.locale.gettext('File {file_name} has just been opened')
                      .replace('{file_name}', str(input_file)))
                return self.fn_get_file_content(file_handler, content_type)
        else:
            print(datetime.utcnow().strftime(self.timestamp_format) + '- ' +
                  self.locale.gettext('File {file_name} does not exist')
                  .replace('{file_name}', str(input_file)))

    def fn_store_file_statistics(self, in_dict):
        in_dict['timer'].start()
        list_file_names = [in_dict['file list']]
        if type(in_dict['file list']) == list:
            list_file_names = in_dict['file list']
        for current_file_name in list_file_names:
            dt_when_last_modified = 'date when last modified'
            file_statistics = str(self.fn_get_file_statistics({
                'file name': current_file_name,
                'checksum included': in_dict['checksum included'],
            }))\
                .replace('date when created', self.locale.gettext('date when created')) \
                .replace(dt_when_last_modified, self.locale.gettext(dt_when_last_modified)) \
                .replace('size [bytes]', self.locale.gettext('size [bytes]')) \
                .replace('Checksum', self.locale.gettext('Checksum'))
            in_dict['logger'].info(self.locale.gettext(
                'File "{file_name}" has the following characteristics: {file_statistics}')
                                   .replace('{file_meaning}', in_dict['file meaning'])
                                   .replace('{file_name}', current_file_name)
                                   .replace('{file_statistics}', file_statistics))
        in_dict['timer'].stop()
