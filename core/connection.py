__author__ = 'mark'

from datetime import datetime
from win32com.client import Dispatch
from threading import Lock
from core.restLogger import logger
TIMEOUT = 600 # seconds
connection_pool_lock = Lock()
connection_pool = []


# qc connection config
qc_config = {
    "URL":"http://137.69.227.80:8080/qcbin/",
    "USER":"yangl8",
    "PASS":"yangl8",
    "DOMAIN":"DEFAULT",
    "PROJECT":"Server"
}

def releaseConnection(qc_connection):
    qc_connection.RefreshConnectionState() # first refresh the status of the connection
    if qc_connection.Connected:
        qc_connection.Disconnect()
    if qc_connection.LoggedIn:
        qc_connection.Logout
    qc_connection.ReleaseConnection()
    logger.info("Release the connection")
    
    
class Connection:
    def __init__(self,qc_connection):
        self.qc_connection = qc_connection
        self.create_time = datetime.now()

    def alive(self):
        _now = datetime.now()
        time_delta = _now - self.create_time
        if time_delta.seconds > TIMEOUT:
            return False
        return True

def get_connection_from_pool():
    global connection_pool
    connection_pool_lock.acquire()
    try:
        if len(connection_pool):
            connection = connection_pool.pop(0)
            if connection.alive():
                logger.info("The connection_pool size is %d and still alive" % len(connection_pool))
                return connection
            else:
                try:
                    releaseConnection(connection._qconnection)
                    del connection
                    logger.info("The connection is overdue , delete from the pool")
                except Exception,e:
                    logger.info(str(e))
        else:
            logger.info("The connection pool is empty , need create a new connection")
    finally:
        connection_pool_lock.release()
        
    _qc_connection = create_qc_connection()
    return Connection(_qc_connection)

def back_connecton_to_pool(connection):
    '''
        return unused connection to the pool
    '''
    global connection_pool
    if not connection:
        return 
    connection_pool_lock.acquire()
    try:
        connection_pool.append(connection)
    finally:
        connection_pool_lock.release()

def create_qc_connection():
    '''Get the hardcoded connection to the server and domain.
    Can be made a "real" engine if you try hard.
    Use makepy utility to determine if the version number has changed (TDApiOle80)
    but this works to current version'''
    qc_connection = Dispatch("TDApiOle80.TDConnection")
    qc_connection.InitConnectionEx(qc_config['URL'])
    qc_connection.login(qc_config['USER'], qc_config['PASS'])
    qc_connection.Connect(qc_config['DOMAIN'], qc_config['PROJECT'])
    return qc_connection


    