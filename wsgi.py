"""
WSGI configuration for PythonAnywhere deployment.
This file tells PythonAnywhere how to load the Flask application.

Copy this file content to: /var/www/gembonganggeredu_pythonanywhere_com_wsgi.py
Or import it from your PythonAnywhere WSGI configuration.
"""
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/gembonganggeredu/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['DB_TYPE'] = 'mysql'

# Import the Flask app - PythonAnywhere requires 'application' variable
from app import create_app

# Create the WSGI application
application = create_app()
