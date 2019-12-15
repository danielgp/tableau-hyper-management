# Change Log for Tableau Hyper Management package

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
