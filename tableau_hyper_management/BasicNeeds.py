"""
BasicNeeds - useful functions library

This library has functions useful to keep main logic short and simple
"""
# standard Python packages
from datetime import datetime, timezone


class BasicNeeds:

    def fn_optional_print(self, boolean_variable, string_to_print):
        if boolean_variable:
            self.fn_timestamped_print(self, string_to_print)

    @staticmethod
    def fn_timestamped_print(self, string_to_print):
        print(datetime.now(timezone.utc).strftime("%Y-%b-%d %H:%M:%S.%f %Z")
              + ' - ' + string_to_print)
