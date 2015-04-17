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
* Flask-FlatPages
* Flask-Script (if run as a standalone script)

Run ``pip install -r requirements.txt`` to install all dependencies.
"""

import datetime

from flask import Flask, render_template, render_template_string
from flask_flatpages import FlatPages, pygmented_markdown
from markupsafe import Markup


# Configuration
# =============

class Config(object):
    u"""The default configuration for the Flask application.

    Only uppercase variables in this class will be stored in the configuration
    object.
    """

    @staticmethod
    def prerender_jinja(text):
        u"""Render Markdown with Jinja directives to HTML.

        Use this function to configure ``FLATPAGES_HTML_RENDERER``, to support
        evaluating Jinja directives embedded within the Markdown document.
        """
        prerendered_body = render_template_string(Markup(text))
        return pygmented_markdown(prerendered_body)

    # Flask-FlatPages configuration
    FLATPAGES_AUTO_RELOAD = False
    FLATPAGES_EXTENSION = '.md'
    FLATPAGES_HTML_RENDERER = prerender_jinja


# Application setup
# =================

application = app = Flask(__name__)
app.config.from_object(Config)
pages = FlatPages(app)


# Template globals & filters
# ==========================

@app.template_global()
def image(src, alt, title='', class_name='', id=''):
    u"""Generate a HTML5 ``figure`` element with an image.

    :param src: the image’s URL.  If it does not start with ``http://`` or
                ``https://``, it is assumed to be a path within the
                ``static/images`` directory.
    :param alt: the text alternative for the image, used as ``alt`` attribute
                on the ``img`` tag.
    :param title: the image’s caption.  If given, a ``figcaption`` element
                  will be added to the ``figure``.
    :param class_name: the CSS class name(s) to be added to the ``figure``
                       element, as a single string.  If empty, no class names
                       will be set.
    :param id: the value of the ``id`` attribute for the ``figure`` element.
               If empty, no ID will be set.
    """
    return render_template('figure.xhtml', src=src, alt=alt, title=title,
                           class_name=class_name, id=id)


@app.template_filter('date')
def format_date(date, format_string):
    u"""Convert a :py:class:`date` or :py:class:`datetime` to a string.

    :param date: the date to be formatted.  If ``None``, it will use the
                 current UTC date and time.
    :param format_string: a string with format codes to control the string
                          representation of the date.  Consult the
                          ``strftime()`` documentation for details.
    """
    if date is None:
        date = datetime.datetime.utcnow()
    return date.strftime(format_string)


# View functions
# ==============

@app.route('/<path:path>/')
def show_page(path):
    u"""Render a static page from the FlatPages collection.

    :param path: the path to the requested page, relative to
                 ``FLATPAGES_ROOT``.
    :raises: :class:`~werkzeug.exceptions.NotFound` if there is no page at the
             given path.
    """
    return render_template('page.xhtml', page=pages.get_or_404(path))


# Error handling
# ==============

@app.errorhandler(404)
def not_found(error):
    u"""Render the “Error 404: Not Found” page."""
    return show_page('error-404'), 404


# Development server
# ==================

if __name__ == '__main__':
    from flask.ext.script import Manager
    app.config.update({'FLATPAGES_AUTO_RELOAD': True})
    manager = Manager(app)
    manager.run()
