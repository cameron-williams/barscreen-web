"""
Utils/helper functions file.
"""
import os
import re
import time

from flask import copy_current_request_context
from flask import request, flash


def read_env(filenames=None, silent=False):
    """
    Read and set environment variables from a .env file
    :param: filenames A string of comma-separated filenames
    If `filenames` is not supplied,
    it will be loaded like: `os.environ.get('ENV', '.env')`
    """
    if not filenames:
        filenames = os.environ.get('ENV', '.env')
    filenames = [f.strip() for f in filenames.split(',')]
    new_vars = {}

    for filename in filenames:
        if not silent:
            print 'Loading environment variables from "%s"...' % filename
        try:
            with open(filename) as f:
                content = f.read()
        except IOError:
            print 'Env file not found:', filename
            return

        for line in content.splitlines():
            m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
            if m1:
                key, val = m1.group(1), m1.group(2)
                m2 = re.match(r"\A'(.*)'\Z", val)
                if m2:
                    val = m2.group(1)
                m3 = re.match(r'\A"(.*)"\Z', val)
                if m3:
                    val = re.sub(r'\\(.)', r'\1', m3.group(1))

                if not silent:
                    print key, '=', val
                new_vars[key] = val

        if not silent:
            print 'Done loading environment variables from "%s".' % filename

    for key, val in new_vars.items():
        os.environ[key] = val
