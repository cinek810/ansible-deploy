"""Module for handling of logging and log files"""

import logging
from logging import handlers as log_han


class CustomFormatter(logging.Formatter):
    """Class adding colours to console logger"""

    def __init__(self, formatter):
        super().__init__()
        grey = "\x1b[0;38m"
        light_green = "\x1b[1;32m"
        yellow = "\x1b[0;33m"
        red = "\x1b[0;31m"
        light_red = "\x1b[1;31m"
        reset = "\x1b[0m"

        self.FORMATS = {
            logging.DEBUG: light_green + formatter + reset,
            logging.INFO: grey + formatter + reset,
            logging.WARNING: yellow + formatter + reset,
            logging.ERROR: red + formatter + reset,
            logging.CRITICAL: light_red + formatter + reset
        }

    def format(self, record):
        """Colour logged message depending on log level"""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class AnsibleDeployerLogger:
    """Class handling creating logger and logging handlers"""

    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    basic_formatter = "%(asctime)s [%(levelname)s]: %(message)s"
    console_formatter = "\n%(asctime)s [%(levelname)s]: %(message)s"
    raw_formatter = "%(message)s"

    def __init__(self, name: str, options: dict):
        self.name = name
        self.options = options
        self.logger = self.create_logger()

    def create_logger(self) -> logging.Logger:
        """Function to create logging objects"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        return logger

    def add_syslog_handler(self):
        """Add syslog handler sending messages through /dev/log"""
        if self.options["syslog"]:
            rsys_handler = log_han.SysLogHandler(address="/dev/log")
            rsys_handler.setFormatter(self.formatter)
            rsys_handler.setLevel(logging.WARNING)
            self.logger.addHandler(rsys_handler)

    def add_memory_handler(self):
        """Add memory handler with hardcoded limit of 15 messages"""
        memory_handler = log_han.MemoryHandler(15, flushLevel=logging.DEBUG, flushOnClose=False)
        memory_handler.setFormatter(self.formatter)
        memory_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(memory_handler)

    def add_console_handler(self, console_formatter_type: str):
        """Add console handler influenced by operator arguments"""
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(console_formatter_type)
                                     if self.options["no_color"]
                                     else CustomFormatter(console_formatter_type))
        console_handler.setLevel(logging.DEBUG if self.options["debug"] else logging.INFO)
        self.logger.addHandler(console_handler)

    def add_file_handler(self, log_path: str, file_formatter_type: str):
        """Function adding file handler to existing logger"""
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(file_formatter_type))
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def flush_memory_handler(self, subcommand_flag: bool, syslog: bool):
        """Flush initial log messages from memory handler to logfile"""
        if syslog:
            # handler[1] - MemoryHandler, handler[3] - FileHandler
            if subcommand_flag:
                self.logger.handlers[1].setTarget(self.logger.handlers[3])
                self.logger.handlers[1].flush()
            self.logger.handlers[1].close()
        else:
            # handler[0] - MemoryHandler, handler[2] - FileHandler
            if subcommand_flag:
                self.logger.handlers[0].setTarget(self.logger.handlers[2])
                self.logger.handlers[0].flush()
            self.logger.handlers[0].close()
