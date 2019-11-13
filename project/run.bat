@echo off
SETLOCAL ENABLEEXTENSIONS
SET variable__path_parent=%~dp0
REM --------------------------------------------------------------------------------------------------------------------
SET variable__path_to_source_files=C:\www\Data\GitRepositories\BitBucket\AutomatedUnitTesting\tests\DataDump\
SET variable__source_file_extension=csv
SET variable__csv_field_separator=;
SET variable__destination_prefix=Prj15172__
REM --------------------------------------------------------------------------------------------------------------------
REM Main part of the script
REM --------------------------------------------------------------------------------------------------------------------
ECHO Any potential leftover Hyper Deamon Log file will be removed to ensure only the current session results will be captured
DEL %variable__path_parent%/hyperd.log
REM --------------------------------------------------------------------------------------------------------------------
SET variable__source_file_base_name=Project_Line_Items__Summary
CALL %variable__path_parent%_functions-Defined.bat :ExecuteTableauHyperMaintenance
SET variable__source_file_base_name=Purchase_Document_For_Project__Summary
CALL %variable__path_parent%_functions-Defined.bat :ExecuteTableauHyperMaintenance
SET variable__source_file_base_name=Budget_Forecast_Actual__Summary
CALL %variable__path_parent%_functions-Defined.bat :ExecuteTableauHyperMaintenance
