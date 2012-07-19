__author__ = 'mark'

import string
from flask import Blueprint,g,json,make_response,abort,request
from core.restLogger import logger

j_encoder = json.JSONEncoder() # json encoder
bp_test_set = Blueprint("bp_testset", __name__) # blueprint

from qcserver import app
from datetime import datetime
j_encoder = json.JSONEncoder()

def get_tstest_from_testset(testname,testset_id):
    testset = g.testset_factory.Item(testset_id)
    tstest_list = testset.TSTestFactory.NewList("")
    for tstest in tstest_list:

        if string.upper(testname) == string.upper(tstest.TestName):
            return tstest   
    return None

@bp_test_set.route('/<int:testset_id>/',methods=['GET','POST'])
@bp_test_set.route('/<int:testset_id>',methods=['GET','POST'])
def get_testset_info_by_id(testset_id):
    '''
        POST :{"testcases" : [ {"id":111 , "name":"caename}] }
    '''
    if testset_id not in app.config['TESTSET_MAP_TESTPLAN']:
        abort(404)
        
    if request.method == "GET":
        testset = g.testset_factory.Item(testset_id)
        testplan = app.config['TESTSET_MAP_TESTPLAN'][testset_id]
        base_url = request.base_url if request.base_url[-1] != "/" else request.base_url[:-1]
        return make_response(j_encoder.encode({
                              'id':testset.ID,\
                              'name':testset.Name,\
                              'testplan':testplan,\
                              'tsinstance_list': base_url + '/tstests'
                              }),200,app.config['JSON_HEADER'])
    
    elif request.method == "POST":
        from core.qio import qc_signal
        testcases = request.json['testcases']
        if len(testcases) == 0:
            qc_signal.send(**{'testset_id':testset_id,'failCaseIds':set()})
            return make_response(j_encoder.encode({"testcases":[]}),200,app.config['JSON_HEADER'])
        
        failCaseIds = set()
        failCasesResp = []
        failCasesCache = []
        for testcase in testcases:
            tstest = get_tstest_from_testset(testcase['name'],testset_id)
            if not tstest:
                failCasesResp.append({"id":"","name":testcase['name'],"lastRun":5})
            else:
                failCasesResp.append({"id":tstest.ID,"name":tstest.TestName,"lastRun":app.config['QC_STATUS'][string.upper(tstest.LastRun.Status)]})
                failCaseIds.add(tstest.ID)
        
                #add data to cache
                failCasesCache.append({"id":tstest.ID,"name":tstest.TestName,"status":"Failed"})
        
        from core.cache import update_fail_cases
        update_fail_cases(testset_id,failCasesCache)
        
        qc_signal.send(**{'testset_id':testset_id,'failCaseIds':failCaseIds}) # send the signal to make the update
        return make_response(j_encoder.encode({"testcases":failCasesResp}),200,app.config['JSON_HEADER'])
        
    
@bp_test_set.route('/<int:testset_id>/tstests')
def get_tstests_info_by_testset_id(testset_id):
    '''
        support 
        1. "/testsets/699/tstests" -> return all tstests result
    '''
    if testset_id not in app.config['TESTSET_MAP_TESTPLAN']:
        abort(404)
    else:
        testset = g.testset_factory.Item(testset_id)
        tstestfactory = testset.TSTestFactory
        tstest_list = tstestfactory.NewList("")
        ts_list =[]
        for tstest in tstest_list:
            ts_list.append({
                            'id':tstest.ID,\
                            'TestID':tstest.TestId,\
                            'testname':tstest.TestName,\
                            'lastRun':app.config['QC_STATUS'][string.upper(tstest.LastRun.Status)]
                            })
        return make_response(j_encoder.encode(ts_list),200,app.config['JSON_HEADER'])
    
@bp_test_set.route('/',methods = ['GET',])
def get_all_testsets():
    '''
        Get all testsets
    '''
    testsets = []
    for testset_id in app.config['TESTSET_MAP_TESTPLAN'].keys():
        testset = g.testset_factory.Item(testset_id)
        testplan = app.config['TESTSET_MAP_TESTPLAN'][testset_id]
        testsets.append({
                              'id':testset.ID,\
                              'name':testset.Name,\
                              'testplan':testplan,\
                              'tsinstance_list': request.base_url +str(testset.ID) + '/tstests'
                            
                        })
        
    return make_response(j_encoder.encode(testsets),200,app.config['JSON_HEADER'])
    
@bp_test_set.route('/<int:testset_id>/bug',methods = ['POST',])    
def upload_bug_testset(testset_id):
    
    testset = g.testset_factory.Item(testset_id)
    tstestfactory = testset.TSTestFactory
    
    try:
        bugFactory = g.qc_connection.BugFactory
        tstestid = request.json['tstestid']
        bugkey = request.json['bugkey']

        bug = bugFactory(None)
        bug.SetField("BG_SEVERITY","3-High")
        bug.SetField("BG_DETECTION_DATE",datetime.now())
        bug.Summary = bugkey
        bug.Post()
        
        tstest = tstestfactory.Item(tstestid)
        bugLink = tstest.BugLinkFactory.AddItem(bug)
        bugLink.LinkType = "Related"
        bugLink.Post()
        
        return make_response(j_encoder.encode({"newbugkey":bugkey}),200,app.config['JSON_HEADER'])
    except Exception,e:
        logger.error(str(e))