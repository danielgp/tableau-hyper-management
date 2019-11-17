# Tableau-Hyper-Management

## What is this repository for?

This repository is intended to manage importing any CSV file into Tableau-Hyper format (to be used with Tableau Desktop/Server) with minimal configuration (as column detection, content type detection and reinterpretation of content are part of the included logic)


## Who do I talk to?

Repository owner is: [Daniel Popiniuc](mailto:daniel.popiniuc@honeywell.com)


## Required software/drivers/configurations

see [this file](readme_software.md)


## Used references

see [this file](readme_reference.md)


## Usage

`python(.exe) <local_path_of_this_package>main.py --input-file <full_path_and_file_base_name_to_file_having_content_as_CSV>(.txt|.csv) --csv-field-separator ,|; --output-file <full_path_and_file_base_name_to_generated_file>(.hyper)`
