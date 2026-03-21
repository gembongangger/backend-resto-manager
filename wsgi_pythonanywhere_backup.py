# ============================================
# BACKUP: PythonAnywhere WSGI Configuration
# ============================================
# Original file: /var/www/gembonganggeredu_pythonanywhere_com_wsgi.py
# Backup date: 2026-03-21
# ============================================
# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.
#
# The below has been auto-generated for your Flask project

import sys

# add your project directory to the sys.path
project_home = '/home/gembonganggeredu/mysite'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# import flask app but need to call it "application" for WSGI to work
from run import app as application  # noqa
