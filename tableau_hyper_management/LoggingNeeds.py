
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
                                                            when = 'h',
                                                            interval = 1,
                                                            backupCount = 5,
                                                            encoding = 'utf-8',
                                                            utc = False)
            # Here we define our formatter
            string_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            log_formatter = logging.Formatter(string_format)
            # Here we set our logHandler's formatter
            log_handler.setFormatter(log_formatter)
            # pairing the handler with logging
            self.logger.addHandler(log_handler)
