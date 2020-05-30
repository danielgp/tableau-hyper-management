"""
localizations_common - common class for various localizations tasks
"""
# package to handle date and times
from datetime import datetime
# package to add support for multi-language (i18n)
import gettext
# glob package
import glob
# package to facilitate operating system project_locale detection
import locale
# package to handle files/folders and related metadata/operations
import os
import pathlib
# package to facilitate multiple operation system operations
import platform


class LocalizationsCommon:
    locale = None
    locale_implemented = [
        'it_IT',
        'ro_RO',
    ]
    operation_is_required = False

    def __init__(self, in_language='en_US'):
        file_parts = os.path.normpath(os.path.abspath(__file__)).replace('\\', os.path.altsep)\
            .split(os.path.altsep)
        locale_domain = file_parts[(len(file_parts)-1)].replace('.py', '')
        locale_folder = os.path.normpath(os.path.join(
            os.path.join(os.path.altsep.join(file_parts), 'project_locale'), locale_domain))
        self.locale = gettext.translation(
            locale_domain, localedir=locale_folder, languages=[in_language], fallback=True)

    def check_file_pairs(self, in_dict):
        get_details_to_operate = False
        file_situation_verdict = ''
        if os.path.lexists(pathlib.Path(in_dict['destination'])):
            source_last_modified = os.path.getmtime(in_dict['source'])
            destination_last_modified = os.path.getmtime(in_dict['destination'])
            if source_last_modified > destination_last_modified:
                self.operation_is_required = True
                get_details_to_operate = True
                print(self.locale.gettext(
                    '#{file_counter}, For locale {locale_name} the {source_file_type} file '
                    + '{source_file_name} is newer than compiled one {destination_file_name}, '
                    + 'therefore to remedy this, {destination_operation_name} is required')
                      .replace('{file_counter}', str(in_dict['counter']))
                      .replace('{locale_name}', in_dict['locale'])
                      .replace('{source_file_type}', in_dict['source file type name'])
                      .replace('{source_file_name}', os.path.basename(in_dict['source']))
                      .replace('{destination_file_name}', os.path.basename(in_dict['destination']))
                      .replace('{destination_operation_name}',
                               in_dict['destination operation name']))
                print(self.locale.gettext('===> source file {source_file_name} '
                                          + 'has {source_last_modified} '
                                          + 'vs. {destination_last_modified} of the '
                                          + 'destination file {destination_file_name}')
                      .replace('{source_file_name}', os.path.basename(in_dict['source']))
                      .replace('{source_last_modified}',
                           str(datetime.fromtimestamp(source_last_modified)))
                      .replace('{destination_last_modified}',
                           str(datetime.fromtimestamp(destination_last_modified)))
                      .replace('{destination_file_name}', os.path.basename(in_dict['destination'])))
                file_situation_verdict = 'newer'
        else:
            self.operation_is_required = True
            get_details_to_operate = True
            print(self.locale.gettext(
                '#{file_counter}, For locale {locale_name} the file {source_file_name}'
                + 'is missing, therefore to remedy this, '
                + '{destination_operation_name} is required into following folder: '
                + '{destination_folder}')
                  .replace('{file_counter}', str(in_dict['counter']))
                  .replace('{locale_name}', in_dict['locale'])
                  .replace('{source_file_name}', os.path.basename(in_dict['source']))
                  .replace('{destination_operation_name}', in_dict['destination operation name'])
                  .replace('{destination_folder}',
                           os.path.normpath(os.path.dirname(in_dict['destination']))))
            file_situation_verdict = 'missing'
        return get_details_to_operate, file_situation_verdict

    @staticmethod
    def file_counter_limit(in_file_counter, in_file_list_size):
        file_list_paring_complete = False
        if in_file_counter == in_file_list_size:
            file_list_paring_complete = True
        return file_list_paring_complete

    def get_region_language_to_use_from_operating_system(self):
        language_to_use = ''
        try:
            region_language_to_use = locale.getdefaultlocale('LC_ALL')
            if region_language_to_use[0] in self.locale_implemented:
                language_to_use = region_language_to_use[0]
        except AttributeError as err:
            print(err)
        except ValueError as err:
            print(err)
        return language_to_use

    @staticmethod
    def get_this_file_folder():
        return os.path.dirname(__file__)

    def get_project_localisation_source_files(self, in_extension):
        file_pattern = os.path.join(os.path.dirname(__file__), '**/*.' + in_extension)
        initial_list = glob.glob(file_pattern, recursive=True)
        normalizer = lambda x: self.path_normalize(x)
        return list(map(normalizer, initial_list))

    @staticmethod
    def get_project_root():
        file_parts = os.path.normpath(os.path.abspath(__file__))\
            .replace('\\', os.altsep).split(os.altsep)
        return os.altsep.join(file_parts[:-3])

    def get_virtual_environment_python_binary(self):
        python_binary = 'python'
        if platform.system() == 'Windows':
            project_root = self.get_project_root()
            join_separator = os.path.altsep
            elements_to_join = [
                project_root,
                'virtual_environment',
                'Scripts',
            ]
            virtual_env_long = join_separator.join(elements_to_join)
            elements_to_join[1] = 'venv'
            virtual_env_short = join_separator.join(elements_to_join)
            if os.path.isdir(virtual_env_long):
                python_binary = os.path.join(virtual_env_long, 'python.exe')
            elif os.path.isdir(virtual_env_short):
                python_binary = os.path.join(virtual_env_short, 'python.exe')
        return os.path.normpath(python_binary)

    def operate_localisation_files(self, in_dict_details_to_operate_with):
        if self.operation_is_required:
            for current_details_to_operate in in_dict_details_to_operate_with:
                os.system(self.get_virtual_environment_python_binary() + ' '
                          + os.path.join(os.path.dirname(__file__), 'localizations_setup.py')
                          + ' ' + current_details_to_operate['operation']
                          + ' --input-file=' + current_details_to_operate['input-file']
                          + ' --output-file=' + current_details_to_operate['output-file']
                          + ' --locale ' + current_details_to_operate['locale']
                          + current_details_to_operate['operation final flags'])

    @staticmethod
    def path_normalize(in_file_name):
        return os.path.join(os.path.normpath(os.path.dirname(in_file_name)),
                            os.path.basename(in_file_name))

    def run_localization_action(self, in_action):
        known_actions = {
            'compile': 'localizations_compile.py',
            'maintain_sources': 'localizations_maintain_sources.py',
        }
        command_parts_to_run = [
            self.get_virtual_environment_python_binary(),
            ' ',
            self.get_this_file_folder(),
            os.path.altsep,
            known_actions.get(in_action),
        ]
        os.system(''.join(command_parts_to_run))
