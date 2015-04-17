#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""The Salzburg Python User Group’s website.

This module contains the entire Salzburg Python User Group’s website as a WSGI
application built on Flask.  It works on both Python 2 and Python 3.  Running
it as a standalone script launches the Flask development web server.

Usage:
  salzpug.py [<port>]

Arguments:
  <port> – The port to listen on (default: 5000)

This module dependes on the following packages:

* Flask

Run ``pip install -r requirements.txt`` to install all dependencies.
"""

import sys

from flask import Flask


# Application setup
# =================

application = app = Flask(__name__)


# Development server
# ==================

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except (IndexError, ValueError):
        port = 5000
    app.run(port=port)
