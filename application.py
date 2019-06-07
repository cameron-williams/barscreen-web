"""
Flask Application for barscreen.
"""
import os, os.path

# Set project directory.
PROJECT_DIR = os.path.dirname(__file__)

from barscreen.app import create_app
app = create_app()
