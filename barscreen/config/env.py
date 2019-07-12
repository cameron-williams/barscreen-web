"""
Env.py

This file holds all env variables that need to be imported.
To add a new environment variable, simple define it and use environ.get("VARIABLE_NAME", "default_value")
e.g
TEST_VARIABLE = environ.get("TEST_VARIABLE", None)
"""
from os import environ

# Flask config settings.
DEBUG = environ.get("DEBUG", False)
SECRET_KEY = environ.get("SECRET_KEY", "DEBUG_KEY")
SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT", "DEBUG_SALT")

# Enable/disable subdomain routing.
SUBDOMAIN_ROUTING = environ.get("SUBDOMAIN_ROUTING", False)

# Database config. If none provided will default to an in memory sqlite database.
DATABASE_URI = environ.get("DATABASE_URL", "sqlite://")

# File upload directory.
UPLOAD_DIR = environ.get("UPLOAD_DIR", "/tmp/upload/")

# Google application credentials. There is weird formatting with the multi-line private key, so the replace is required for json.loads to work on it.
GOOGLE_APPLICATION_CREDENTIALS = environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").replace("'", '"')