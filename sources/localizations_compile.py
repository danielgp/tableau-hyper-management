"""
localization_setup - facilitates localization file compilation (from .po to .mo)
"""
import glob
import os
import pathlib
# package to facilitate multiple operation system operations
import platform


class CustomizedLocalizationCompiling:

    def compile_localisation_files(self, compilation_needed, domains_to_compile):
        if compilation_needed:
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

    @staticmethod
    def evaluate_compilation_necessity(in_list_localisation_source_files):
        localisation_compilation_is_required = False
        file_list_paring_complete = False
        file_counter = 0
        domains_to_compile = []
        compiling_files_counter = 0
        while not file_list_paring_complete:
            get_domain_details_for_compilation = False
            source_localisation_file = in_list_localisation_source_files[file_counter]
            compiled_localisation_file = source_localisation_file.replace('.po', '.mo')
            folder_parts = pathlib.PurePath(source_localisation_file).parts
            current_locale = folder_parts[(len(folder_parts) - 3)]
            if os.path.lexists(pathlib.Path(compiled_localisation_file)):
                source_last_modified = os.path.getmtime(source_localisation_file)
                compiled_last_modified = os.path.getmtime(compiled_localisation_file)
                if source_last_modified > compiled_last_modified:
                    localisation_compilation_is_required = True
                    get_domain_details_for_compilation = True
                    print('#' + str(file_counter) + ', '
                          + 'For locale ' + current_locale + ' source file '
                          + os.path.basename(source_localisation_file)
                          + ' is newer than compiled one '
                          + os.path.basename(compiled_localisation_file)
                          + ' so compilation needs to take place to remedy this')
                    print('===>' + source_localisation_file + ' has ' + str(source_last_modified)
                          + ' vs. ' + str(compiled_last_modified))
            else:
                get_domain_details_for_compilation = True
                print('#' + str(file_counter) + ', '
                      + 'The file ' + os.path.basename(source_localisation_file)
                      + ' does not have compiled file for ' + current_locale
                      + ' therefore will require compiling into the same folder: '
                      + os.path.dirname(source_localisation_file))
                localisation_compilation_is_required = True
            if get_domain_details_for_compilation:
                domains_to_compile.append(compiling_files_counter)
                domains_to_compile[compiling_files_counter] = {
                    'input-file': source_localisation_file,
                    'output-file': compiled_localisation_file,
                    'locale': current_locale,
                }
                compiling_files_counter += 1
            file_counter += 1
            if file_counter == len(in_list_localisation_source_files):
                file_list_paring_complete = True
        return localisation_compilation_is_required, domains_to_compile

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
            python_binary = 'python.exe'
        return os.path.normpath(os.path.join(
                os.path.dirname(__file__)
                    .replace('sources', 'virtual_environment/Scripts') \
                    .replace('/', os.altsep),
                python_binary))

    def path_normalize(self, in_file_name):
        return os.path.join(os.path.normpath(os.path.dirname(in_file_name)),
                            os.path.basename(in_file_name))


my_class = CustomizedLocalizationCompiling()

locale_source_files = my_class.get_project_localisation_source_files()
compilation_is_required, compiling_domains = \
    my_class.evaluate_compilation_necessity(locale_source_files)
my_class.compile_localisation_files(compilation_is_required, compiling_domains)
