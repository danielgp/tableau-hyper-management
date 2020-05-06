"""
localization_setup - facilitates localization file compilation (from .po to .mo)
"""
import glob
import os
import pathlib

file_pattern = os.path.join(os.path.dirname(__file__), '**/*.po')\
    .replace('/test', '/sources')\
    .replace('\\', '/')
list_localisation_source_files = glob.glob(file_pattern, recursive=True)
localisation_compilation_is_required = False
file_list_complete = False
domains_to_compile = []
file_counter = 0
compiling_files_counter = 0
while not file_list_complete:
    get_domain_details_for_compilation = False
    current_file = list_localisation_source_files[file_counter].replace('/', '\\')
    compiled_localisation_file = current_file.replace('.po', '.mo')
    folder_parts = os.path.dirname(current_file).split('\\')
    current_locale = folder_parts[(len(folder_parts)-2)]
    if os.path.lexists(pathlib.Path(compiled_localisation_file)):
        source_last_modified = os.path.getmtime(current_file)
        compiled_last_modified = os.path.getmtime(compiled_localisation_file)
        if source_last_modified > compiled_last_modified:
            localisation_compilation_is_required = True
            get_domain_details_for_compilation = True
            print('#' + str(file_counter) + ', '
                  + 'For locale ' + current_locale + ' source file '
                  + os.path.basename(current_file)
                  + ' is newer than compiled one '
                  + os.path.basename(compiled_localisation_file)
                  + ' so compilation needs to take place to remedy this')
            print('===>' + current_file + ' has ' + str(source_last_modified)
                  + ' vs. ' + str(compiled_last_modified))
    else:
        get_domain_details_for_compilation = True
        print('#' + str(file_counter) + ', '
              + 'For locale ' + current_locale + ' does not exists, '
              + 'therefore will require compiling, so '
              + os.path.basename(current_file)
              + ' will be used to generate '
              + os.path.basename(compiled_localisation_file)
              + ' in the same folder: ' + os.path.dirname(current_file))
        localisation_compilation_is_required = True
    if get_domain_details_for_compilation:
        domains_to_compile.append(compiling_files_counter)
        domains_to_compile[compiling_files_counter] = {
            'input-file': current_file,
            'output-file': compiled_localisation_file,
            'locale': current_locale,
        }
        compiling_files_counter += 1
    file_counter += 1
    if file_counter == len(list_localisation_source_files):
        file_list_complete = True
project_root = os.path.dirname(__file__).replace('/sources', '')
compiler_binary = os.path.join(
    os.path.dirname(__file__)\
        .replace('sources', 'virtual_environment/Scripts')\
        .replace('/', '\\'),
    'python.exe')
if localisation_compilation_is_required:
    for current_domain_to_compile in domains_to_compile:
        os.system(compiler_binary + ' '
                  + os.path.join(os.path.dirname(__file__), 'localizations_setup.py')
                  + ' compile_catalog'
                  + ' --input-file=' + current_domain_to_compile['input-file']
                  + ' --output-file=' + current_domain_to_compile['output-file']
                  + ' --locale ' + current_domain_to_compile['locale']
                  + ' --statistics')
else:
    print('For all Localization source files there is a pair of compiled localization file '
          + 'which has same date or newer, so no compiling is necessary!')
