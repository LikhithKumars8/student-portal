import logging
import datetime
import os


PATH_FILE_NAME = f"api_requests_{datetime.datetime.now().date()}.log"

def get_logger():
    logging.basicConfig(filename=os.path.join('logs', PATH_FILE_NAME),level=logging.DEBUG)
    return logging

def api_logging(log_data):
    logger = get_logger()
    """
    Function used to log all the API requests and responses along with error if any.
    Creates log files on daily basis.
    Params:
    1. log_data: list of individual logs having log type and message.
    """
    try:
        for log in log_data:
            message = log.split("|| ")
            if message[0] == 'info':
                logger.info(message[1])
            else:
                logger.error(message[1])
    except Exception as e:
        logger.error(f"Log function error: {str(e)}")
    logger.info("=" * 150)
    return True