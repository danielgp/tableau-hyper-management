"""
localization_setup - facilitates localization file compilation (from .po to .mo)
"""
import glob
import os
import pathlib
# package to facilitate multiple operation system operations
import platform


class CustomizedLocalizationCompiling:
    localisation_compilation_is_required = False

    def check_file_pairs(self, in_dict):
        get_domain_details_for_compilation = False
        if os.path.lexists(pathlib.Path(in_dict['compiled'])):
            source_last_modified = os.path.getmtime(in_dict['source'])
            compiled_last_modified = os.path.getmtime(in_dict['compiled'])
            if source_last_modified > compiled_last_modified:
                self.localisation_compilation_is_required = True
                get_domain_details_for_compilation = True
                print('#' + str(in_dict['counter']) + ', '
                      + 'For locale ' + in_dict['locale'] + ' source file '
                      + os.path.basename(in_dict['source'])
                      + ' is newer than compiled one '
                      + os.path.basename(in_dict['compiled'])
                      + ' so compilation needs to take place to remedy this')
                print('===>' + in_dict['source'] + ' has ' + str(source_last_modified)
                      + ' vs. ' + str(compiled_last_modified))
        else:
            self.localisation_compilation_is_required = True
            get_domain_details_for_compilation = True
            print('#' + str(in_dict['counter']) + ', '
                  + 'The file ' + os.path.basename(in_dict['source'])
                  + ' does not have compiled file for ' + in_dict['locale']
                  + ' therefore will require compiling into the same folder: '
                  + os.path.dirname(in_dict['source']))
        return get_domain_details_for_compilation

    def compile_localisation_files(self, domains_to_compile):
        if self.localisation_compilation_is_required:
            for current_domain_to_compile in domains_to_compile:
                os.system(self.get_virtual_environment_python_binary() + ' '
                          + os.path.join(os.path.dirname(__file__), 'localizations_setup.py')
                          + ' compile_catalog'
                          + ' --input-file=' + current_domain_to_compile['input-file']
                          + ' --output-file=' + current_domain_to_compile['output-file']
                          + ' --locale ' + current_domain_to_compile['locale']
                          + ' --statistics')
        else:
            print('For all Localization source files there is a pair of compiled localization file '
                  + 'which has same date or newer, so no compiling is necessary!')

    def evaluate_compilation_necessity(self, in_list_localisation_source_files):
        list_size = len(in_list_localisation_source_files)
        self.localisation_compilation_is_required = False
        file_list_paring_complete = False
        file_counter = 0
        domains_to_compile = []
        compiling_files_counter = 0
        while not file_list_paring_complete:
            source_localisation_file = in_list_localisation_source_files[file_counter]
            folder_parts = pathlib.PurePath(source_localisation_file).parts
            current_locale = folder_parts[(len(folder_parts) - 3)]
            fn_dict = {
                'compiled': source_localisation_file.replace('.po', '.mo'),
                'counter': file_counter,
                'locale': current_locale,
                'source': source_localisation_file,
            }
            get_domain_details_for_compilation = self.check_file_pairs(fn_dict)
            if get_domain_details_for_compilation:
                domains_to_compile.append(compiling_files_counter)
                domains_to_compile[compiling_files_counter] = {
                    'input-file': fn_dict['source'],
                    'output-file': fn_dict['compiled'],
                    'locale': fn_dict['locale'],
                }
                compiling_files_counter += 1
            file_counter += 1
            file_list_paring_complete = self.file_counter_limit(file_counter, list_size)
        return domains_to_compile

    @staticmethod
    def file_counter_limit(in_file_counter, in_file_list_size):
        file_list_paring_complete = False
        if in_file_counter == in_file_list_size:
            file_list_paring_complete = True
        return file_list_paring_complete

    @staticmethod
    def get_project_localisation_source_files():
        file_pattern = os.path.join(os.path.dirname(__file__), '**/*.po') \
            .replace('test', 'sources')
        initial_list = glob.glob(file_pattern, recursive=True)
        normalizer = lambda x: my_class.path_normalize(x)
        return list(map(normalizer, initial_list))

    @staticmethod
    def get_project_root():
        return os.path.normpath(os.path.dirname(__file__).replace('sources', ''))

    @staticmethod
    def get_virtual_environment_python_binary():
        python_binary = 'python'
        if platform.system() == 'Windows':
            virtual_env_long = os.path.normpath(os.path.dirname(__file__)
                                                .replace('sources', 'virtual_environment/Scripts'))
            virtual_env_short = os.path.normpath(os.path.dirname(__file__)
                                                 .replace('sources', 'venv/Scripts'))
            if os.path.isdir(virtual_env_long):
                python_binary = os.path.join(virtual_env_long, 'python.exe')
            elif os.path.isdir(virtual_env_short):
                python_binary = os.path.join(virtual_env_short, 'python.exe')
        return python_binary

    def path_normalize(self, in_file_name):
        return os.path.join(os.path.normpath(os.path.dirname(in_file_name)),
                            os.path.basename(in_file_name))


my_class = CustomizedLocalizationCompiling()

locale_source_files = my_class.get_project_localisation_source_files()
compiling_domains = my_class.evaluate_compilation_necessity(locale_source_files)
my_class.compile_localisation_files(compiling_domains)
