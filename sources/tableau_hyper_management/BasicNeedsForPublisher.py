"""
Class Publisher Specific Needs

Handling specific needs for Publisher script
"""
# package to facilitate common operations
from tableau_hyper_management.BasicNeeds import BasicNeeds


class BasicNeedsForPublisher:
    lcl_bn = None

    def __init__(self):
        self.lcl_bn = BasicNeeds()

    def fn_check_inputs_specific(self, input_parameters):
        self.lcl_bn .fn_validate_single_value(input_parameters.input_file,
                                              'file', 'input file')
        self.lcl_bn .fn_validate_single_value(input_parameters.input_credentials_file,
                                              'file', 'credentials file')
        self.lcl_bn .fn_validate_single_value(input_parameters.tableau_server,
                                              'url', 'Tableau Server URL')
