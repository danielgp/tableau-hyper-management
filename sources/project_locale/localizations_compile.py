"""
localization_compile - facilitates localization file compilation (from .po to .mo)
"""
import os
import pathlib

# specific to this project
from localizations_common import LocalizationsCommon


class CustomizedLocalizationCompiling(LocalizationsCommon):
    localisation_compilation_is_required = False

    def evaluate_compilation_necessity(self, in_list_localisation_source_files):
        list_size = len(in_list_localisation_source_files)
        self.operation_is_required = False
        file_list_paring_complete = False
        file_counter = 0
        domains_to_compile = []
        compiling_files_counter = 0
        while not file_list_paring_complete:
            source_localisation_file = in_list_localisation_source_files[file_counter]
            folder_parts = pathlib.PurePath(source_localisation_file).parts
            current_locale = folder_parts[(len(folder_parts) - 3)]
            fn_dict = {
                'destination': source_localisation_file.replace('.po', '.mo'),
                'counter': file_counter,
                'locale': current_locale,
                'source': source_localisation_file,
                'source file type name': 'source',
                'destination operation name': 'compilation',
            }
            operation_check_result, operation_to_execute = self.check_file_pairs(fn_dict)
            if operation_check_result:
                domains_to_compile.append(compiling_files_counter)
                domains_to_compile[compiling_files_counter] = {
                    'input-file': fn_dict['source'],
                    'operation': 'compile_catalog',
                    'operation final flags': ' --statistics',
                    'output-file': fn_dict['destination'],
                    'locale': fn_dict['locale'],
                }
                compiling_files_counter += 1
            file_counter += 1
            file_list_paring_complete = self.file_counter_limit(file_counter, list_size)
        return domains_to_compile


my_class = CustomizedLocalizationCompiling()

locale_source_files = my_class.get_project_localisation_source_files('po')
operation_locale_dict = my_class.evaluate_compilation_necessity(locale_source_files)
my_class.operate_localisation_files(operation_locale_dict)
