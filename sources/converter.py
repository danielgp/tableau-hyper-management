"""
main - entry point of the package

This file is performing CSV read into HYPER file and measures time elapsed (performance)
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
    class_lc = LocalizationsCommon()
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
    # as input and/or output file might contain CalculatedDate expression
    # an evaluation is required
    class_pn.parameters.input_file = class_pn.class_ph.eval_expression(
        class_pn.class_ln.logger, class_pn.parameters.input_file, 7)
    class_pn.parameters.output_file = class_pn.class_ph.eval_expression(
        class_pn.class_ln.logger, class_pn.parameters.output_file, 7)
    # as destination folder could be dynamic and not existent safety measure is required
    destination_folder = os.path.dirname(class_pn.parameters.output_file)
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    # check if proceeding is necessary
    load_data_frame_necessary = True
    if class_pn.parameters.input_file_format != 'hyper' \
        and class_pn.parameters.output_file_format == 'hyper' \
            and class_pn.parameters.policy_to_handle_hyper_file == 'create':
        if os.path.isfile(class_pn.parameters.output_file):
            # initial assumption is no further load is necessary
            load_data_frame_necessary = False
            relevant_files_list = []
            feedback = [
                'The output file defined as {file_name} already exists',
                'As handle hyper action is set to "create", '
                + 'further checks will happen to ensure none of the source files '
                + 'is newer than destination',
            ]
            for crt_feedback in feedback:
                class_pn.class_ln.logger.error(class_pn.locale.gettext(
                    crt_feedback.replace('{file_name}', class_pn.parameters.output_file)))
                class_pn.class_bn.fn_timestamped_print(class_pn.locale.gettext(
                    crt_feedback.replace('{file_name}', class_pn.parameters.output_file)))
    # Even if the Hyper file exists already, can happen one of the source file is newer
    # so an overwrite might be more appropriate in such case
    # identify all files matching input file information
    relevant_files_list = class_pn.class_fo.fn_build_file_list(
        class_pn.class_ln.logger, class_pn.timer, class_pn.parameters.input_file)
    # log file statistic details
    class_pn.class_fo.fn_store_file_statistics({
            'file list': relevant_files_list,
            'file meaning': 'Input',
            'checksum included': class_pn.parameters.include_checksum_in_files_statistics,
            'logger': class_pn.class_ln.logger,
            'timer': class_pn.timer,
    })
    # further could be required to assess "load_data_frame_necessary" value
    if not load_data_frame_necessary:
        final_verdict = class_pn.source_vs_destination_file_modification_assesment(
            class_pn.class_ln.logger, class_pn.timer, {
                'destination file': class_pn.parameters.output_file,
                'list source files': relevant_files_list,
            })
        # as final_verdict values could be different depending on localization used/detected
        # only a check of None or not None is possible
        if final_verdict is not None:
            load_data_frame_necessary = True
            class_pn.parameters.policy_to_handle_hyper_file = 'overwrite'
    # instantiate Tableau Hyper Api Extra Logic class
    class_thael = TableauHyperApiExtraLogic(language_to_use)
    # loading from a specific folder all files matching a given pattern into a data frame
    input_dict = {
        'action': class_pn.parameters.policy_to_handle_hyper_file,
        'compression': class_pn.parameters.input_file_compression,
        'field delimiter': class_pn.parameters.csv_field_separator,
        'file list': relevant_files_list,
        'format': class_pn.parameters.input_file_format,
        'name': 'irrelevant',
        'query': class_pn.parameters.sql_query_to_handle_data,
        'schema name': 'Extract',
        'table name': 'Extract',
    }
    working_data_frame = None
    if class_pn.parameters.input_file_format == 'hyper':
        if relevant_files_list:
            input_dict['action'] = 'read from existing hyper'
            input_dict['hyper file'] = relevant_files_list[0]
            working_data_frame = class_thael.fn_hyper_handle(
                class_pn.class_ln.logger, class_pn.timer, input_dict)
    elif load_data_frame_necessary:
        working_data_frame = class_pn.class_dio.fn_load_file_into_data_frame(
            class_pn.class_ln.logger, class_pn.timer, input_dict)
    if working_data_frame is not None:
        output_dict = input_dict
        # overwrite few important values with relevant information for output
        output_dict['file list'] = 'irrelevant'
        output_dict['format'] = class_pn.parameters.output_file_format
        output_dict['name'] = class_pn.parameters.output_file
        output_dict['compression'] = class_pn.parameters.output_file_compression
        if class_pn.parameters.input_file_format.lower() == 'hyper':
            tuple_supported_file_types = class_thael.supported_output_file_types
        else:
            tuple_supported_file_types = class_pn.class_dio.implemented_disk_write_file_types
        wanted_output_format = class_pn.parameters.output_file_format.lower()
        if class_pn.parameters.output_file_format.lower() in tuple_supported_file_types:
            class_pn.class_dio.fn_store_data_frame_to_file(
                class_pn.class_ln.logger, class_pn.timer, working_data_frame, output_dict)
            # store statistics about output file
            class_pn.class_fo.fn_store_file_statistics({
                'file list': class_pn.parameters.output_file,
                'file meaning': 'Generated',
                'checksum included': class_pn.parameters.include_checksum_in_files_statistics,
                'logger': class_pn.class_ln.logger,
                'timer': class_pn.timer,
            })
        elif wanted_output_format == 'hyper':
            supported_types = class_thael.supported_input_file_types
            if class_pn.parameters.input_file_format.lower() in supported_types:
                c_td = TypeDetermination(language_to_use)
                fn_dict = {
                    'action': input_dict['action'],
                    'data frame': working_data_frame,
                    'input parameters': class_pn.parameters,
                    'input data types': class_pn.config['data_types'],
                    'hyper file': class_pn.parameters.output_file,
                    'schema name': input_dict['schema name'],
                    'table name': input_dict['table name'],
                }
                if fn_dict['action'] in ('append', 'create', 'overwrite'):
                    # advanced detection of data type within Data Frame
                    fn_dict['data frame structure'] = c_td.fn_get_data_frame_structure(
                        class_pn.class_ln.logger, class_pn.timer, fn_dict)
                    # determine Hyper Table Columns
                    fn_dict['hyper table columns'] = class_thael.fn_build_hyper_columns(
                        class_pn.class_ln.logger, class_pn.timer, fn_dict['data frame structure'])
                    # The rows to insert into the <hyper_table> table.
                    fn_dict['data'] = class_thael.fn_rebuild_data_frame_content_for_hyper(
                        class_pn.class_ln.logger, class_pn.timer, fn_dict)
                    # check if output Hyper file does not exists
                    # and if so action will be always "overwrite"
                    # which will trigger internal Hyper structure creation (schema and table)
                    if not os.path.isfile(fn_dict['hyper file']):
                        fn_dict['action'] = 'overwrite'
                # manipulate destination Tableau Extract (Hyper)
                class_thael.fn_hyper_handle(class_pn.class_ln.logger, class_pn.timer, fn_dict)
                # store statistics about output file
                class_pn.class_fo.fn_store_file_statistics({
                    'file list': class_pn.parameters.output_file,
                    'file meaning': 'Generated',
                    'checksum included': class_pn.parameters.include_checksum_in_files_statistics,
                    'logger': class_pn.class_ln.logger,
                    'timer': class_pn.timer,
                })
            else:
                class_pn.class_ln.logger.error(
                    class_pn.locale.gettext(
                        'Only certain file types are supported as input file type '
                        + 'in combination with Tableau Extract (Hyper) as output file type. '
                        + 'And {given_file_type} is not among "{supported_file_types}"')
                        .replace('{given_file_type}', wanted_output_format)
                        .replace('{supported_file_types}', '", "'.join(supported_types)))
    # just final message
    class_pn.class_bn.fn_final_message(
        class_pn.class_ln.logger, class_pn.parameters.output_log_file,
        class_pn.timer.timers.total(SCRIPT_NAME))
