"""
This module provides record_log functions for logging.
"""

from pathlib import Path

import logging

from .caller_definer import define_caller

PATH_TO_LOG = Path(__file__).parent / 'log.log'

logging.basicConfig(
    filename = PATH_TO_LOG, 
    filemode = "a", 
    format = "(%(asctime)s) %(message)s", 
    level = logging.INFO, 
    datefmt = '%d-%m-%y %H:%M:%S',
    encoding = "UTF-8",
)

def record_log(record_text : str, source : str = None, is_error : bool = False, error_type : type = None) -> None:
    """
    Saves record into log.log

    In case of error during logging prints (through print function) error of logging with passed parameters 
    
    Formats of record:
    -----------------
    (time('%d-%m-%y %H:%M:%S')) [{source}]: {record_text}
    (time('%d-%m-%y %H:%M:%S')) [{source}]: error {error_type}: {record_text} 

    Parameters:
    -----------
    record_text : str
        text to log
    source : str
        initiator's name of action. if source is not passed, then source is relative-module path to caller 
    is_error : bool
        logic flag: is error-record?
    error_type : type
        type of happened error
    
    Returns:
    --------
        None
    """

    try:
        if source is None:
            source = define_caller()

        if is_error:
            message_to_log = f"""[{source}]: error {error_type}: {record_text}"""
            logging.error(msg = message_to_log)        
        else:
            message_to_log = f"""[{source}]: {record_text}"""
            logging.info(msg = message_to_log)
        
        if __debug__:
            print(message_to_log) 

    except Exception as log_error:
        print(f"LOGGER ERROR (type: {type(log_error)}): {log_error}, {record_text=} {source=} {is_error=} {error_type=}")

record_log("Log initializing", "")