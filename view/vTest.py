__author__ = 'mark'

from flask import Blueprint,g,abort,json,make_response
from core.restLogger import logger

j_encoder = json.JSONEncoder()

bp_test = Blueprint('bp_test',__name__)

from qcserver import app

@bp_test.route('/<int:test_id>/',methods = ['GET'])
@bp_test.route('/<int:test_id>',methods = ['GET'])
def get_test_by_id(test_id):
    try: 
        test = g.test_factory.Item(test_id)
        return make_response(j_encoder.encode({
                                               'id':test.ID,\
                                               'name':test.Name,\
                                               'path':test.FullPath}),200,app.config['JSON_HEADER'])
    except Exception,e:
        abort(404)