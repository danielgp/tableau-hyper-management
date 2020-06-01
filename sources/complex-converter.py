"""
This file is performing multiple data strctured files into HYPER file targeting multiple tables
"""
# package to handle files/folders and related metadata/operations
import os
# Custom classes specific to this package
from project_locale.localizations_common import LocalizationsCommon
from tableau_hyper_management.ProjectNeeds import ProjectNeeds
from tableau_hyper_management.TableauHyperApiExtraLogic import TableauHyperApiExtraLogic
from tableau_hyper_management.TypeDetermination import TypeDetermination
# get current script name
SCRIPT_NAME = os.path.basename(__file__).replace('.py', '')

# main execution logic
if __name__ == '__main__':
    # instantiate Localizations Common class
    class_lc = LocalizationsCommon('en_US')
    # ensure all localization templates files older than translated files
    class_lc.run_localization_action('maintain_sources')
    # ensure all compiled localization files are in place (as needed for localized messages later)
    class_lc.run_localization_action('compile')
    # establish localization language to use
    language_to_use = class_lc.get_region_language_to_use_from_operating_system()
    # instantiate Extractor Specific Needs class
    class_pn = ProjectNeeds(SCRIPT_NAME, language_to_use)
    # load application configuration (inputs are defined into a json file)
    class_pn.load_configuration()
    # adding a special case data type
    class_pn.config['data_types']['empty'] = '^$'
    class_pn.config['data_types']['str'] = ''
    # initiate Logging sequence
    class_pn.initiate_logger_and_timer()
    # reflect title and input parameters given values in the log
    class_pn.class_clam.listing_parameter_values(
        class_pn.class_ln.logger, class_pn.timer, 'Tableau Hyper Converter',
        class_pn.config['input_options'][SCRIPT_NAME], class_pn.parameters)
    ### WIP - start
    # instantiate Tableau Hyper Api Extra Logic class
    class_thael = TableauHyperApiExtraLogic(language_to_use)
    # instantiate Type Determination class
    c_td = TypeDetermination(language_to_use)
    # load JSON from specified import export sequence file
    import_export_sequence = class_pn.class_fo.fn_open_file_and_get_content(
        class_pn.parameters.import_export_sequence_file)
    for crt_ie_sequence in import_export_sequence:
        table_counter = 0
        if crt_ie_sequence['sequence-type'] == 'import-files-into-hyper':
            for crt_input in crt_ie_sequence['input-content']:
                for crt_table in crt_input['tables']:
                    action_to_apply = 'append'
                    if table_counter == 0:
                        action_to_apply = 'overwrite'
                    table_counter += 1
                    df_dict = {
                        'format': crt_table['input-file']['format'],
                        'file list': [crt_table['input-file']['name']],
                        'name': 'irrelevant',
                    }
                    if 'compression' in crt_table['input-file']:
                        df_dict['field delimiter'] = crt_table['input-file']['compression']
                    if 'field-delimiter' in crt_table['input-file']:
                        df_dict['field delimiter'] = crt_table['input-file']['field-delimiter']
                    working_data_frame = class_pn.class_dio.fn_load_file_into_data_frame(
                        class_pn.class_ln.logger, class_pn.timer, df_dict)
                    df_dict = None
                    fn_dict = {
                        'action': action_to_apply,
                        'data frame': working_data_frame,
                        'hyper file': crt_ie_sequence['output-file']['name'],
                        'input data types': class_pn.config['data_types'],
                        'input parameters': class_pn.parameters,
                        'schema name': crt_input['schema-name'],
                        'table name': crt_table['table-name'],
                    }
                    working_data_frame = None
                    # advanced detection of data type within Data Frame
                    fn_dict['data frame structure'] = c_td.fn_get_data_frame_structure(
                        class_pn.class_ln.logger, class_pn.timer, fn_dict)
                    # determine Hyper Table Columns
                    fn_dict['hyper table columns'] = class_thael.fn_build_hyper_columns(
                        class_pn.class_ln.logger, class_pn.timer, fn_dict['data frame structure'])
                    # The rows to insert into the <hyper_table> table.
                    fn_dict['data'] = class_thael.fn_rebuild_data_frame_content_for_hyper(
                        class_pn.class_ln.logger, class_pn.timer, fn_dict)
                    class_thael.fn_hyper_handle(class_pn.class_ln.logger, class_pn.timer, fn_dict)
                    fn_dict = None
                    class_thael.columns_for_hyper_conversion = {}
    ### WIP - end
    # just final message
    class_pn.class_bn.fn_final_message(
        class_pn.class_ln.logger, class_pn.parameters.output_log_file,
        class_pn.timer.timers.total(SCRIPT_NAME))
