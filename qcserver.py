__author__ = 'mark'

from flask import Flask,redirect

app = Flask(__name__) # create the application instance
app.config.from_object('config')

from view.vTest import bp_test
from view.vTestSet import bp_test_set
from view.vAdmin import bp_admin
from core.httpUtil import *

app.debug = True

@app.route('/')
def index():
    return redirect('/admin')

app.register_blueprint(bp_test,url_prefix = "/tests")
app.register_blueprint(bp_test_set,url_prefix = "/testsets")
app.register_blueprint(bp_admin,url_prefix = "/admin")

if __name__ == "__main__":
    app.run()