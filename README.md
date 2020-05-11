# Tableau-Hyper-Management

## Code quality analysis and Build Status
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/danielgp/tableau-hyper-management/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/danielgp/tableau-hyper-management/?branch=master)
[![Build Status](https://scrutinizer-ci.com/g/danielgp/tableau-hyper-management/badges/build.png?b=master)](https://scrutinizer-ci.com/g/danielgp/tableau-hyper-management/build-status/master)

## What is this repository for?

Based on [Tableau Hyper API](https://help.tableau.com/current/api/hyper_api/en-us/) this repository is intended to manage importing any CSV file into Tableau-Hyper format (to be used with Tableau Desktop/Server) with minimal configuration (as column detection, content type detection and reinterpretation of content are part of the included logic), therefore speed up the process of building extract.

Also a publishing data source script allows to take resulted Tableau Hyper file and publish it to a Tableau Server, therefore automating the tedious task to refresh data on the server side (of course, only relevant in case no direct connection from Tableau Server to data source is possible or nature of content is not supported directly by data source: one real-life example can be daily snapshot of a dynamically changing content to capture big variations in time).

## Who do I talk to?

Repository owner is: [Daniel Popiniuc](mailto:danielpopiniuc@gmail.com)

## Implemented features

- conversion intake data from a single or multiple CSV files based on a single input parameter (can be specific or contain a file pattern);
- dynamic fields detection based ont 1st line content and provided field separator (strategic advantage);
- dynamic advanced content type detection covering following data types: integer, float-dot, date-iso8601, date-DMY-dash, date-DMY-dot, date-DMY-slash, date-MDY, date-MDY-medium, date-MDY-long, time-12, time-12-micro-sec, time-24, time-24-micro-sec, datetime-iso8601, datetime-iso8601-micro-sec, datetime-MDY, datetime-MDY-micro-sec, datetime-MDY-medium, datetime-MDY-medium-micro-sec, datetime-MDY-long, datetime-MDY-long-micro-sec, string;
- support for empty field content for any data type (required re-interpreting CSV to be accepted by Hyper Inserter to ensure INT or DOUBLE data types are considered);
- use Panda package to benefit of Data Frames speed and flexibility;
- log file to capture entire logic details (very useful for either traceability but also debugging);
- most of the logic actions are not timed for performance measuring so you can plan better your needs;
- publishing a Tableau Extract (Hyper format) to a Tableau Server (specifying Site and Project);
- detection of operating system current region language and log all feedback details using that.

## Combinations of file types supported

| Input (down) File Type/Format Output (right) | Comma Separated Values | Excel              | Pickle             | Tableau Extract (Hyper) |
|:---------------------------------------------|:----------------------:|:------------------:|:------------------:|:-----------------------:|
| Comma Separated Values                       | :heavy_check_mark:     | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark:      |
| Excel                                        | :heavy_check_mark:     | :heavy_check_mark: | :heavy_check_mark: | :no_entry:              |
| Tableau Extract (Hyper)                      | :no_entry:             | :no_entry:         | :no_entry:         | :no_entry:              |
| Pickle                                       | :heavy_check_mark:     | :heavy_check_mark: | :heavy_check_mark: | :soon:                  |

## Installation

Installation can be completed in few steps as follows:
* Ensure you have git available to your system:
```
    $ git --version
```
> If you get an error depending on your system you need to install it.
>> For Windows you can do so from [Git for Windows](https://github.com/git-for-windows/git/releases/);
* Download this project from Github:
```
    $ git clone https://github.com/danielgp/tableau-hyper-management <local_path_of_this_package>
```
> conventions used:
>> <content_within_html_tags> = variables to be replaced with user values relevant strings
* Create a Python Virtual Environment using following command executed from project root folder:
```
    $ python(.exe) -m venv <local_folder_on_your_computer_for_this_package>/virtual_environment/
```
* Upgrade pip (PIP is a package manager for Python packages) and SetupTools using following command executed from newly created virtual environment and Scripts sub-folder:
```
    $ <local_path_of_this_package>/virtual_environment/Scripts/python(.exe) -m pip install --upgrade pip
    $ <local_path_of_this_package>/virtual_environment/Scripts/pip(.exe) install --upgrade setuptools
```
* Install project prerequisites using following command executed from project root folder:
```
    $ <local_path_of_this_package>/virtual_environment/Scripts/python(.exe) <local_path_of_this_package>/setup.py install
```
* Ensure all localization source files are compile properly in order for the package to work properly
```
    $ <local_path_of_this_package>/virtual_environment/Scripts/python(.exe) <local_path_of_this_package>/sources/localizations_compile.py
```

## Maintaining local package up-to-date

Once the package is installed is quite important to keep up with latest releases as such are addressing important code improvements and potential security issues, and this can be achieved by following command:
```
    $ git --work-tree=<local_path_of_this_package> --git-dir=<local_path_of_this_package>/.git/ --no-pager pull origin master
```
- conventions used:
    - <content_within_html_tags> = variables to be replaced with user values relevant strings


## Usage


### Converting CSV file into Tableau Extract (Hyper format)
```
    $ <local_path_of_this_package>/virtual_environment/Scripts/python(.exe) <local_path_of_this_package>/tableau_hyper_management/converter.py --input-file <full_path_and_file_base_name_to_file_having_content_as_CSV> --input-file-format csv|excel|json|pickle --input-file-compression infer|bz2|gzip|xz|zip --csv-field-separator ,|; --output-file <full_path_and_file_base_name_to_generated_file>(.hyper) --output-file-format csv|excel|hyper|json|pickle --output-file-compression infer|bz2|gzip|xz|zip (--output-log-file <full_path_and_file_name_to_log_running_details>) (--unique-values-to-analyze-limit 100|200=default_value_if_omitted|500|1000)
```
- conventions used:
    - (content_within_round_parenthesis) = optional
    - <content_within_html_tags> = variables to be replaced with user values relevant strings
    - single vertical pipeline = separator for alternative options 


### Publishing a Tableau Extract (Hyper format) to a Tableau Server
```
    $ <local_path_of_this_package>/virtual_environment/Scripts/python(.exe) <local_path_of_this_package>/tableau_hyper_management/publish_data_source.py --input-file <full_path_and_file_base_name_with_tableau_extract>(.hyper) --tableau-server <tableau_server_url> --tableau-site <tableau_server_site_to_publish_to> --tableau-project <tableau_server_project_to_publish_to> --publishing-mode Append|CreateNew|Overwrite==default_if_omitted --input-credentials-file %credentials_file% (--output-log-file <full_path_and_file_name_to_log_running_details>)
```
- conventions used:
    - (content_within_round_parenthesis) = optional
    - <content_within_html_tags> = variables to be replaced with user values relevant strings
    - single vertical pipeline = separator for alternative options

## Change Log / Releases detailed

see [CHANGE_LOG.md](CHANGE_LOG.md)

## Planned features to add (of course, when time will permit / help would be appreciated / votes|feedback is welcomed)

- additional formats to be recognized, like:
    - float-USA-thousand-separator,
    - float-EU,
    - float-EU-thousand-separator;
    - geographical identifiers (Country, US - Zip Codes)

## Features to request template

Use [feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)


## Required software/drivers/configurations

see [readme_software.md](readme_software.md)


## Used references

see [readme_reference.md](readme_reference.md)
