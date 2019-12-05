"""
BasicNeeds - useful functions library

This library has functions useful to keep main logic short and simple
"""

class BasicNeeds:

    def fn_optional_print(boolean_variable, string_to_print):
        if boolean_variable:
            print(string_to_print)
