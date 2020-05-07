"""
LoggingNeeds

This library sets all required parameters for a rotating LOG file
"""
from datetime import datetime
# package for Log management
import logging
import logging.handlers as handlers


class LoggingNeeds:
    logger = None

    def initiate_logger(self, logger_file_name, logger_internal_name):
        # initiate Logging
        self.logger = logging.getLogger(logger_internal_name)
        # set logging level to desired level only if specified
        if logger_file_name == 'None':
            self.logger.setLevel(logging.NOTSET)
        else:
            self.logger.setLevel(logging.DEBUG)
            # defining log file and setting rotating logic
            log_handler = handlers.TimedRotatingFileHandler(logger_file_name,
                                                            when='h',
                                                            interval=1,
                                                            backupCount=5,
                                                            encoding='utf-8',
                                                            utc=True)
            # ensure timestamps are reported as UTC time-zone
            my_converter = lambda x, y: datetime.utcnow().timetuple()
            logging.Formatter.converter = my_converter
            # Here we define our formatter
            log_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            # Here we set our logHandler's formatter
            log_handler.setFormatter(log_formatter)
            # pairing the handler with logging
            self.logger.addHandler(log_handler)
