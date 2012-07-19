__author__ = 'mark'

import pythoncom
from flask import g,json,make_response,request,abort
from qcserver import app
from connection import get_connection_from_pool,back_connecton_to_pool
from core.restLogger import logger

j_encoder = json.JSONEncoder() # the json encode instance

@app.before_request
def app_before_request():
    if request.method != "GET":
        '''
            it the method is not get , check the media type should be appication/json
        '''
        content_type = request.headers.get('Content-Type',None)
        if not content_type or content_type != 'application/json':
            abort(415)
                  
    pythoncom.CoInitialize() # init for each request
    g.connection = get_connection_from_pool()
    g.qc_connection = g.connection.qc_connection
    g.test_factory = g.qc_connection.TestFactory
    g.testset_factory = g.qc_connection.TestSetFactory
    g.tree_manager = g.qc_connection.TreeManager
    
@app.after_request
def app_after_request(resp):
    back_connecton_to_pool(g.connection)
    pythoncom.CoUninitialize() # uninit for each request
    return resp

@app.errorhandler(401)
def notfound(e):
    return make_response(j_encoder.encode({"code":401,\
                                           "errmsg":"Missing the authorization in the http headers"}),\
                                            401,{'Content-Type':'application/json'})
    
@app.errorhandler(404)
def notfound(e):
    return make_response(j_encoder.encode({"code":404,\
                                           "errmsg":"The object not found"}),\
                                            404,{'Content-Type':'application/json'})


@app.errorhandler(415)
def internal_error(e):
    return make_response(j_encoder.encode({"code":500,\
                                           "errmsg":"Unsupported meida type , please use application/json"}),\
        415,{'Content-Type':'application/json'})
    
@app.errorhandler(500)
def internal_error(e):
    logger.error(e)
    return make_response(j_encoder.encode({"code":500,\
                                           "errmsg":str(e)}),\
        500,{'Content-Type':'application/json'})