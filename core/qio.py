__author__ = 'mark'

from blinker import Namespace
from datetime import datetime
from threading import Thread
import pythoncom
from core.restLogger import logger


# the aio is based on the flask io
io_signals = Namespace()
qc_write_signal = io_signals.signal("qc_write") # the qc write signal


class Qc_Signal:
    def __init__(self,sender):
        self.sender = sender
        self.connect()

    def send(self,**kwargs):
        qc_write_signal.send(self.sender,**kwargs)
        logger.info("Send the signal to , param = %s" % kwargs)

    def connect(self):
        qc_write_signal.connect(self.do,self.sender)

    def do(self,sender,**kwargs):
        qcthread = WriteTestSetProcess(kwargs['testset_id'],kwargs['failCaseIds'])
        qcthread.start()
        logger.info("Start the thread to write the qc result" )
        
from qcserver import app
qc_signal = Qc_Signal(app)

from core.connection import get_connection_from_pool,back_connecton_to_pool
class WriteTestSetProcess(Thread):
    def __init__(self,testset_id,failCaseIds):
        Thread.__init__(self)
        self.testset_id = testset_id
        self.failCaseIds = failCaseIds

    def run(self):
        pythoncom.CoInitialize()
        connection = get_connection_from_pool()
        qc_connection = connection.qc_connection
        test_factory = qc_connection.TestFactory
        testset_factory = qc_connection.TestSetFactory
        tree_manager = qc_connection.TreeManager
        
        start_time = datetime.now()
        print start_time
        try:
            testset = testset_factory.Item(self.testset_id)
            tstest_list = testset.TSTestFactory.NewList("")
            for tstest in tstest_list:
                _runFactory = tstest.RunFactory
                _newRun = _runFactory.AddItem(None)
                if tstest.ID in self.failCaseIds:
                    _newRun.Status = 'FAILED'
                else:
                    _newRun.Status = 'PASSED'

                _newRun.Name = tstest.TestName
                _newRun.Post()

                tstest.Status = _newRun.Status
                tstest.Post()
        
            logger.info("Finish the write thread ,duration time = %s" % (datetime.now() - start_time))
        except Exception,e:
            logger.error(str(e))
        finally:
            back_connecton_to_pool(connection)
            pythoncom.CoUninitialize()
        
        