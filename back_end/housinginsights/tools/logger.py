import os, logging

python_filepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               os.pardir, os.pardir))
logging_path = os.path.abspath(os.path.join(python_filepath, "logs"))

class HILogger():
    """
    Log to console and to file.
    logger = HILogger(name=__name__, logfile=mylog.log)
    """

    DEFAULT_FORMAT = '%(levelname)s -- %(asctime)s -- %(name)s -- %(message)s'
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, name, logfile=None, fmt=DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT,
                level=logging.INFO):
        # Get config values

        if logfile:
            self.logfile = os.path.join(logging_path, logfile)

        # Create Logger, Formatter, and StreamHandler
        logger = logging.getLogger(os.path.basename(name))
        logger.handlers = []

        logger.setLevel(level)
        formatter = logging.Formatter(  fmt=fmt,
                                        datefmt=datefmt)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        if logfile:
            file_handler = logging.FileHandler(self.logfile)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        self.logger = logger


    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

    def set_level(self, level):
        self.logger.setLevel(level)
