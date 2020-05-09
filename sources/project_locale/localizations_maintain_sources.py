"""
localization_update - facilitates localization file maintenance
"""
import os

from localizations_common import LocalizationsCommon


class LocalizationsMaintainSources(LocalizationsCommon):

    def evaluate_update_necessity(self, in_list_localisation_source_files):
        list_size = len(in_list_localisation_source_files)
        self.operation_is_required = False
        file_list_paring_complete = False
        file_counter = 0
        domains_locale_to_update = []
        compiling_files_counter = 0
        while not file_list_paring_complete:
            template_localisation_file = in_list_localisation_source_files[file_counter]
            for current_locale in self.locale_implemented:
                join_separator = os.path.altsep
                elements_to_join = [
                    os.path.dirname(template_localisation_file),
                    current_locale,
                    'LC_MESSAGES',
                    os.path.basename(template_localisation_file).replace('.pot', '.po'),
                ]
                fn_dict = {
                    'destination': join_separator.join(elements_to_join),
                    'counter': file_counter,
                    'locale': current_locale,
                    'source': template_localisation_file,
                    'source file type name': 'template',
                    'destination operation name': 'update',
                }
                operation_check_result, file_situation_verdict = self.check_file_pairs(fn_dict)
                operation_to_execute = ''
                operation_final_flags = ''
                if 'missing' in file_situation_verdict:
                    operation_to_execute = 'init_catalog'
                    operation_final_flags = ' --previous'
                elif 'newer' in file_situation_verdict:
                    operation_to_execute = 'update_catalog'
                if operation_check_result:
                    domains_locale_to_update.append(compiling_files_counter)
                    domains_locale_to_update[compiling_files_counter] = {
                        'input-file': fn_dict['source'],
                        'operation': operation_to_execute,
                        'operation final flags': operation_final_flags,
                        'output-file': fn_dict['destination'],
                        'locale': fn_dict['locale'],
                    }
                    compiling_files_counter += 1
            file_counter += 1
            file_list_paring_complete = self.file_counter_limit(file_counter, list_size)
        return domains_locale_to_update


my_class = LocalizationsMaintainSources()

locale_source_files = my_class.get_project_localisation_source_files('pot')
operation_locale_dict = my_class.evaluate_update_necessity(locale_source_files)
my_class.operate_localisation_files(operation_locale_dict)
