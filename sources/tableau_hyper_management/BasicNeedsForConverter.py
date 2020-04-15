"""
Class Converter Specific Needs

Handling specific needs for Extractor script
"""
# package to handle files/folders and related metadata/operations
import os.path
# package to facilitate common operations
from tableau_hyper_management.BasicNeeds import BasicNeeds


class BasicNeedsForConverter:
    lcl_bn = None

    def __init__(self):
        self.lcl_bn = BasicNeeds()

    def fn_check_inputs_specific(self, input_parameters):
        self.fn_validate_single_value(os.path.dirname(input_parameters.output_file),
                                      'folder', 'output file')
