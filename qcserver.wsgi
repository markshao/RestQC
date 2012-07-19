import os
import sys

project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0,project_dir)

from qcserver import app as application