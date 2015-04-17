#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""The Salzburg Python User Group’s website.

This module contains the entire Salzburg Python User Group’s website as a WSGI
application built on Flask.  It works on both Python 2 and Python 3.  Running
it as a standalone script launches the Flask development web server via the
Flask-Script extension.

Usage:
  * salzpug.py runserver [-h <host>] [-p <port>] [-d] [-r]
  * salzpug.py shell
  * salzpug.py --help

Options:
  -h <host>  the hostname to listen on (default: 127.0.0.1)
  -p <port>  the port of the web server (default: 5000)
  -d         use the Werkzeug debugger
  -r         reload the web server if the script changes

This module dependes on the following packages:

* Flask
* Flask-Script (if run as a standalone script)

Run ``pip install -r requirements.txt`` to install all dependencies.
"""

from flask import Flask


# Application setup
# =================

application = app = Flask(__name__)


# Development server
# ==================

if __name__ == '__main__':
    from flask.ext.script import Manager
    manager = Manager(app)
    manager.run()
