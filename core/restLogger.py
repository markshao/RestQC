__author__ = 'mark'

import logging
import os

logger_dir = os.path.join(os.path.dirname(__file__)[:-4],'log')
logger_path = os.path.join(logger_dir,'qc_server.log')

# check the enviroment
if not os.path.exists(logger_dir):
    os.mkdir(logger_dir)


log_level = logging.DEBUG

def getLogger(logger):
    file_handler = logging.FileHandler(filename=logger_path)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s [module=%(module)s:line=%(lineno)d]: %(message)s '
    ))
    logger.addHandler(file_handler)
    logger.setLevel(log_level)
    return logger,file_handler

# make the code adaptable
class RestLogger:
    '''
        To solve the repeat log problem
    '''
    def __init__(self,name):
        self.logger = logging.getLogger(name)
        
    def info(self,msg):
        logger,file_handler = getLogger(self.logger)
        logger.info(msg)
        logger.removeHandler(file_handler)
        
    def debug(self,msg):
        logger,file_handler = getLogger(self.logger)
        logger.debug(msg)
        logger.removeHandler(file_handler)
        
    def error(self,msg):
        logger,file_handler = getLogger(self.logger)
        logger.error(msg)
        logger.removeHandler(file_handler)
        
        
logger = RestLogger("test_qa")