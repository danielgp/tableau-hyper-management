call %*
GOTO END

:ExecuteTableauHyperMaintenance
    ECHO -------------------------------------------------------------------------------------------------------
    ECHO Running Tableau Hyper Maintenance from command line for %variable__path_to_source_files%%variable__source_file_base_name%.%variable__source_file_extension%
    ECHO .......
    python.exe %variable__path_parent%main.py --input-file %variable__path_to_source_files%%variable__source_file_base_name%.%variable__source_file_extension% --csv-field-separator %variable__csv_field_separator% --output-file %variable__path_to_source_files%%variable__destination_prefix%%variable__source_file_base_name%.hyper
GOTO END

:END
