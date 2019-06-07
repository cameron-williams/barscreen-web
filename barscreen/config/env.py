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

