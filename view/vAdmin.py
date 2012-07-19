__author__ = 'mark'

from flask import Blueprint,g,abort,render_template
from core.restLogger import logger
from config import *
import string

bp_admin = Blueprint('bp_admin',__name__)

from qcserver import app
from core.cache import fail_cases_by_project

def get_nav_list_for_project(active_key = None):
    class PrjNav:
        def __init__(self,name,id):
            self.id = id
            self.name = name
            self.active = None
    
    nav_list = []    
    for key ,value in TESTSET_MAP_TESTPLAN.iteritems():
        nav = PrjNav(value,key)
        if key == active_key:
            nav.active = True
        
        nav_list.append(nav)
        
    return nav_list


@bp_admin.route('/',methods = ['GET'])
def get_test_by_id():
    return render_template("base.html")

@bp_admin.route('/bugreport',methods = ['GET'])
def bugreport_main():
    nav_list = get_nav_list_for_project()
    return render_template("admin/bugreport/bugreport.html",nav_list = nav_list)

@bp_admin.route('/bugreport/testsets/<int:testset_id>',methods = ['GET'])
def bugreport_by_testset(testset_id):
    nav_list = get_nav_list_for_project(testset_id)
    
    failTests = fail_cases_by_project.get(testset_id,[])
    
    testset = g.testset_factory.Item(testset_id)
    tstestfactory = testset.TSTestFactory
    
    for failtest in failTests:
        tstest = tstestfactory.Item(failtest['id'])
        bugkey = getBugKey(tstest)
        failtest['bugkey'] = bugkey
    
    return render_template("admin/bugreport/bug_report_by_testset.html",nav_list = nav_list,failTests=failTests,bugurl = "/testsets/%s/bug" % testset_id)


def getBugKey(tsinstance):
    buglist = tsinstance.BugLinkFactory.NewList("")
    if not buglist or len(buglist) == 0:
        return None
    else:
        bug = buglist[len(buglist) - 1].TargetEntity
        return bug.Summary