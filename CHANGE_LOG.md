# Change Log for Tableau Hyper Management package

## Version 1.5.2 release on 2020-05-30
- implemented localization maintenance besides existing compilation + added localization to localization common class;
- reflecting JSON file format support in documentation; 


## Version 1.5.1 release on 2020-05-29
- added an extra verification for the scenario when at least one of the source files is newer than destination "overwrite" decision will be stronger than given "create" (safer to data accuracy).

## Version 1.5.0 release on 2020-05-26
- extended functionality and now input file and/or output file are aware of Calculated Date expressions, making possible this way to use dynamic name interpreted at run time;
- added "create" as option for "policy-to-handle-hyper-file" input parameter that allows skipping recreating "hyper" file if already exists;
- improved feedback. 

## Version 1.4.9 release on 2020-05-19
- bug fixes on internal code structure.

## Version 1.4.8 release on 2020-05-17
- extended the sql input parameter to be used in conjunction with Read action, this way a user customized query can be used to extract partial data (besides existing full extract one)
- few internal code and localization messages enhancements and corrections.

## Version 1.4.7 release on 2020-05-17
- added a data remove feature from Tableau Extract file (Hyper format) by extending one of the input parameters and add an additional one to have the ability to specify a custom SQL to remove data based on customer needs.

## Version 1.4.6 release on 2020-05-17
- added additional input parameter to have be able to create (or recreate if hyper file already exists) new hyper file and add data from input files OR just use existing hyper file and append data from input files (can be very useful in case of large data sets).  

## Version 1.4.5 release on 2020-05-15
- added support for 2 additional file format in a combination with output file format = Hyper;
- few additional file formats combination checks to avoid runtime errors;
- improved localized feedback captured in log files.

## Version 1.4.2 release on 2020-05-12
- supported files are now used internally for validation purposes which makes code more maintainable if and when new file types will be implemented with changes in fewer places.

## Version 1.4.1 release on 2020-05-12
- added support for Parquet file format (full coverage: both input and output).

## Version 1.4.0 release on 2020-05-12
- extended support for Pickle and JSON file format which now can be used as input files in combination with Tableau Extract (Hyper) as output file;
- field type timestamp properly recognized;
- added a matrix of file combination in documentation (should make usage much clearer).

## Version 1.3.14 release on 2020-05-11
- tweaked the localization logic that manages language to use based on operating system default region language.

## Version 1.3.13 release on 2020-05-10
- forced a value to be string converted when logged.

## Version 1.3.12 release on 2020-05-09
- region language detection improved.

## Version 1.3.11 release on 2020-05-07
- internal project restructure.

## Version 1.3.10 release on 2020-05-07
- added localisation (currently covering en_US, it_IT, ro_RO locales);
- operating system current region locale is auto-detected and if 
- added support to convert Excel, Pickle and JSON formats into CSV;
- revised internal code towards a more manageable one.

## Version 1.2.16 release on 2020-04-04
- added input and output (where relevant) file statistics to log;
- code cleanup;

## Version 1.2.15 release on 2020-04-03
- implemented input validation for most important values;
- corrected internal package name in the setup file;

## Version 1.2.14 release on 2020-04-01
- updating README file to reflect recent file name change;
- minor code tweaks;

## Version 1.2.13 not released, skipped
- skipped (13...)

## Version 1.2.12 released on 2020-04-01
- minor code tweaks
- renamed `publisher.py` to `publish_data_source.py`;

## Version 1.2.11 released on 2020-04-01
- renamed `main.py` to `converter.py` (apologies for any inconvenience this may create to any user);
- various internal code quality improvements; 


## Version 1.2.10 released on 2020-03-31
- internal code change

## Version 1.2.9 released on 2020-03-31
- just corrected setup.py

## Version 1.2.8 released on 2020-03-31
- just corrected setup.py

## Version 1.2.7 released on 2020-03-30
- added a file existing check to circumvent a package crash in case of file not existing;
- added support for large input file;
- added support for upper case months and weekdays besides existing proper case;
- added timing for certain code performance masuring (that is exposing such information to logger);
- bumped version of TableauHypeAPI (former 0.0.9746 => new 0.0.10309 which was released on 2020-03-25);
- added additional script to facilitate publishing a Tableau Extract file (Hyper format) to a specified Tableau Server.

## Version 1.2.6 released on 2020-03-05
- bug fix to get only non-null unique values analyzed in case of a float column that may hold disguised integers

## Version 1.2.5 released on 2020-03-05
- internal code tweaks to reduce complexity for one long method

## Version 1.2.4 released on 2020-03-05
- updated download source URL for Tableau Hyper API

## Version 1.2.3 released on 2020-03-05
- added boolean data type
- added an optional log file to ease debugging activity when necessary
- bumped version of TableauHypeAPI to 0.0.9746 (which is now available on [pypi.org](https://pypi.org/) as [tableauhyperapi](https://pypi.org/project/tableauhyperapi/))

## Version 1.2.2 released on 2020-01-20
- internal code optimizations
- switched default behavior to store 0 values instead of nulls in case of integer determined fields

## Version 1.2.1 released on 2019-12-22
- just reflecting new version of Tableau Hyper API (former 0.0.8952 => new 0.0.9273)

## Version 1.2.0 released on 2019-12-15
- additional data type formats recognized:
    - date-DMY-dash;
    - date-DMY-dot;
    - date-DMY-slash;
    - date-MDY-medium;
    - date-MDY-long;
    - datetime-MDY;
    - datetime-MDY-micro-sec;
    - datetime-MDY-medium;
    - datetime-MDY-medium-micro-sec;
    - datetime-MDY-long; 
    - datetime-MDY-long-micro-sec;
- various code optimizations:
    - eliminating data type as method parameters and using original class variable;
    - moved data type determination to main program logic and out of the Hyper creation one = segregation of duties;
    - split analyzing method into 2 separate parts, one for very first unique value and another methods for rest;
    - switch to a more standardized class name in the main logic.

## Version 1.1.0 released on 2019-12-05
- switch the handler of user input parameters from getopt to argparse package (greater flexibility, shorter code, easier future maintenance)

## Version 0.8.0 released on 2019-11-24
- switch from classic loops to Pandas way of handling data manipulation
