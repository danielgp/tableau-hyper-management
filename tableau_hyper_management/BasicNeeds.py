"""
BasicNeeds - useful functions library

This library has functions useful to keep main logic short and simple
"""

# standard Python packages
from datetime import datetime, timezone
import json
import os.path


class BasicNeeds:
    cfg_dtls = {}

    def fn_load_configuration(self):
        with open(os.path.dirname(__file__) + "/config.json", 'r') as json_file:
            self.cfg_dtls = json.load(json_file)
            self.cfg_dtls['data_types']['empty'] = ''
            self.cfg_dtls['data_types']['str'] = '.'

    def fn_optional_print(self, boolean_variable, string_to_print):
        if boolean_variable:
            self.fn_timestamped_print(self, string_to_print)

    @staticmethod
    def fn_timestamped_print(self, string_to_print):
        print(datetime.now(timezone.utc).strftime("%Y-%b-%d %H:%M:%S.%f %Z")
              + ' - ' + string_to_print)
