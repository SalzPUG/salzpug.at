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
* Pygments

Run ``pip install -r requirements.txt`` to install all dependencies.
"""

import datetime
import math

from flask import (Flask, render_template, render_template_string, request,
                   url_for, abort)
from flask_flatpages import FlatPages, pygmented_markdown, pygments_style_defs
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
    PYGMENTS_STYLE = 'tango'

    # Custom configuration
    ARTICLES_PER_PAGE = 3


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


@app.template_global()
def pagination_url(page):
    u"""Return the current view’s URL, using a different ``page`` parameter.

    All parameters and arguments of the current URL other than ``page`` will
    remain the same. This is useful for paginated views that split their
    contents over several pages.

    :param page: the new value for the ``page`` parameter of the current
                 view’s URL.
    """
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


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

@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>/')
def index(page):
    u"""Render a page with all articles in reversed chronological order.

    Configure ``ARTICLES_PER_PAGE`` to control how many articles shall be
    displayed on one page.
    """
    articles = blog_articles()
    pagination = Pagination(articles, page, app.config['ARTICLES_PER_PAGE'])
    if not pagination.items and page != 1:
        abort(404)
    return render_template('index.xhtml', pagination=pagination)


@app.route('/<path:path>/')
def show_page(path):
    u"""Render a static page from the FlatPages collection.

    :param path: the path to the requested page, relative to
                 ``FLATPAGES_ROOT``.
    :raises: :class:`~werkzeug.exceptions.NotFound` if there is no page at the
             given path.
    """
    return render_template('page.xhtml', page=pages.get_or_404(path))


@app.route('/archives/')
def archives():
    u"""Render a page with the titles of all articles, grouped by year."""
    return render_template('archives.xhtml', articles=blog_articles())


@app.route('/pygments.css')
def pygments_css():
    u"""Return the stylesheet for the selected Pygments style."""
    style = app.config['PYGMENTS_STYLE']
    return pygments_style_defs(style), 200, {'Content-Type': 'text/css'}


# Error handling
# ==============

@app.errorhandler(404)
def not_found(error):
    u"""Render the “Error 404: Not Found” page."""
    return show_page('error-404'), 404


# Auxiliary functions
# ===================

def blog_articles():
    u"""Return all blog articles in reversed chronological order.

    An “article” is supposed to be a page from the FlatPages collection that
    has the “published” attribute in its metadata.
    """
    return reversed(sorted((p for p in pages if 'published' in p.meta),
                           key=lambda p: p.meta['published']))


# Pagination
# ==========

class Pagination(object):
    u"""A simple class to paginate an iterable.

    This class is inspired by Armin Ronacher’s snippet at
    http://flask.pocoo.org/snippets/44/.
    """

    def __init__(self, iterable, page, per_page):
        u"""Create a new ``Pagination`` object.

        :param iterable: the iterable to paginate.
        :param page: the current page number.
        :param per_page: the number of items of the iterable to put on each
                         page.
        """
        self.all_items = list(iterable)
        self.page = page
        self.per_page = per_page

    @property
    def items(self):
        u"""All items of the iterable that are on the current page.

        >>> pagination = Pagination('ABCDEFGHIJKLMNOPQRS', page=5, per_page=2)
        >>> pagination.items
        ['I', 'J']
        """
        lower_index = (self.page-1) * self.per_page
        upper_index = self.page * self.per_page
        return self.all_items[lower_index:upper_index]

    @property
    def pages(self):
        u"""The total number of pages.

        >>> pagination = Pagination('ABCDEFGHIJKLMNOPQRS', page=5, per_page=2)
        >>> pagination.pages
        10
        """
        return int(math.ceil(len(self.all_items) / float(self.per_page)))

    @property
    def has_prev(self):
        u"""``True`` if the current page is not the first page.

        >>> pagination = Pagination('ABCDEFGHIJKLMNOPQRS', page=5, per_page=2)
        >>> pagination.has_prev
        True
        """
        return self.page > 1

    @property
    def has_next(self):
        u"""``True`` if the current page is not the last page.

        >>> pagination = Pagination('ABCDEFGHIJKLMNOPQRS', page=5, per_page=2)
        >>> pagination.has_next
        True
        """
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        u"""Return an iterator yielding page numbers to build a pagination.

        This function returns numbers similar to the builtin ``range()``,
        starting at ``1``, but omitting superfluous page numbers inbetween.
        “Holes” within the sequence are denoted by a single ``None`` value.

        >>> pagination = Pagination('ABCDEFGHIJKLMNOPQRS', page=5, per_page=2)
        >>> list(pagination.iter_pages(left_current=1, right_current=1))
        [1, 2, None, 4, 5, 6, None, 9, 10]

        :param left_edge: the number of page numbers to yield at the beginning
                          of the pagination.
        :param left_current: the number of page numbers to yield before the
                             current page.
        :param right_current: the number of page numbers to yield after the
                              current page.
        :param right_edge: the number of page numbers to yield at the end of
                           the pagination.
        """
        last = 0
        for i in range(1, self.pages+1):
            if (i <= left_edge or i > self.pages-right_edge or
                    self.page-left_current-1 < i <= self.page+right_current):
                if last + 1 != i:
                    yield None
                yield i
                last = i


# Development server
# ==================

if __name__ == '__main__':
    from flask.ext.script import Manager
    app.config.update({'FLATPAGES_AUTO_RELOAD': True})
    manager = Manager(app)
    manager.run()
