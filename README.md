# Tableau-Hyper-Management

## What is this repository for?

This repository is intended to manage importing any CSV file into Tableau-Hyper format (to be used with Tableau Desktop/Server) with minimal configuration (as column detection, content type detection and reinterpretation of content are part of the included logic)


## Who do I talk to?

Repository owner is: [Daniel Popiniuc](mailto:daniel.popiniuc@honeywell.com)


## Usage

`python(.exe) <local_path_of_this_package>main.py --input-file <full_path_and_file_base_name_to_file_having_content_as_CSV>(.txt|.csv) --csv-field-separator ,|; --output-file <full_path_and_file_base_name_to_generated_file>(.hyper)`

- conventions used:
    - (content_within_round_paranthesis) = optional
    - <content_within_html_tags> = variables to be replaced with user values relevant strings
    - single vertical pipeline = separator for alternative options 

## Implemented features

- dynamic fields detection based ont 1st line content and provided field separator;
- content type detection:
    - integer,
    - float-USA,
    - date-iso8601,
    - date-USA,
    - time-24,
    - time-24-us,
    - time-USA,
    - time-USA-us,
    - datetime-iso8601,
    - datetime-iso8601-us,
    - string;
- support for empty field content for any data type (required re-interpreting CSV to be accepted by Hyper Inserter);

## Planned features to add (of course, when time will permit / help would be appreciated / votes|feedback is welcomed)

- additional formats to be recognized, like:
    - date-USA-medium;
    - date-USA-long;
    - float-USA-thousand-separator,
    - float-EU,
    - float-EU-thousand-separator;
- feedback localization;
- CSV file internationalization;


## Features to request template

Use [feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)


## Required software/drivers/configurations

see [readme_software.md](readme_software.md)


## Used references

see [readme_reference.md](readme_reference.md)
