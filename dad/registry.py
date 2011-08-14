# Copyright (C) 2011  Lincoln de Sousa <lincoln@comum.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Implements a _very_ simple resource registry

This module reads information stored in the `resources/resources.json'
file and some bits of `conf.py' to generate the includes lines for js
and css resources needed by templates.

Read the resource file to know more about the format and how to add or
remove a resource in a template.
"""

from json import loads
from flask import url_for, Markup
import conf

# Yes, if you change your resources file, you'll need tou restart the
# flask development web server.
RESOURCES = loads(file(conf.RESOURCES_FILE).read())


# Dict with kinds of data we know how to handle
HANDLERS = {
    'css': '<link type="text/css" rel="stylesheet" href="%s">',
    'js': '<script type="text/javascript" src="%s"></script>'
}


def devresources(ext, group):
    """Returns an iterator containing all includes of such an `ext' that
    are present in a given `group'
    """
    checkext = lambda n: n if n.endswith('.%s' % ext) else '%s.%s' % (n, ext)
    resources = RESOURCES[ext].get('__all__', []) + RESOURCES[ext][group][:]
    return ((HANDLERS[ext] % checkext(url_for('static', filename=res))
            for res in resources))


def prodresource(ext, name):
    """Returns a single include of a resource with such an `ext' and
    with a given `name'.

    Maybe `name' is an incorrect way of defining it. The idea behind
    this registry is to give the possibility to separate resources by
    their features.

    This way, the `_gallery.js' file is not meant to be used only in the
    `gallery.html' template, but in all templates that actually needs a
    gallery.
    """
    name = '_%s.%s' % (name, ext)
    if conf.STATIC_URL is not None:
        url = conf.STATIC_URL % name
    else:
        url = url_for('static', filename=name)
    return HANDLERS[ext] % url


def js(group):
    """Just a shortcut to generate includes for js scripts in a given
    `group'.
    """
    if conf.ENV == 'production':
        return prodresource('js', group)
    return Markup(''.join(devresources('js', group)))


def css(group):
    """Just a shortcut to generate includes for css files in a given
    `group'.
    """
    if conf.ENV == 'production':
        return prodresource('css', group)
    return Markup(''.join(devresources('css', group)))
