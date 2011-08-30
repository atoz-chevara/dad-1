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

from math import ceil
from time import mktime
from flask import Flask, Response, render_template as render, request, abort
from model import Message
from mongoengine import ValidationError
from json import dumps, loads
import registry
import conf

app = Flask(__name__)


def render_template(name, **attrs):
    """Alias used to update the dict with attrs passed to the _real_
    template renderer function. Currently, we're only passing the
    resource registry to all templates.
    """
    attrs.update({ 'registry': registry })
    return render(name, **attrs)


def paginate(collection, maxperpage=10):
    page = int(request.values.get('p', 1))-1
    maxperpage = int(request.values.get('max', maxperpage))
    count = float(collection.count())
    pagecount = int(ceil(count / maxperpage))
    skip = maxperpage * page
    limit = maxperpage * page + maxperpage
    return {
        'collection': collection[skip:limit],
        'count': count,
        'pagecount': pagecount,
        'previous': False if page == 0 else max(1, page),
        'current': page+1,
        'next': page+2 if pagecount > page+1 else False,
        }


def img(iid, size, fit=True):
    size = tuple(int(x) for x in size.split('x'))
    msg = Message.objects.with_id(iid)
    resp = Response(msg.thumb(size, fit), content_type='image/png')
    resp.last_modified = mktime(msg.date.timetuple())
    return resp


@app.route('/')
def index():
    return render_template('simple/index.html', Message=Message, conf=conf)


@app.route('/gallery')
def gallery():
    return render_template(
        'simple/gallery.html',
        slideshow=paginate(Message.slideshow, conf.GALLERY_MAX_PERPAGE))


@app.route('/messages')
def messages():
    return render_template(
        'simple/messages.html',
        Message=Message,
        slideshow=paginate(
            Message.objects.order_by('-date'),
            conf.MESSAGES_MAX_PERPAGE))


@app.route('/about')
def about():
    return render_template('simple/about.html')


@app.route('/tou')
def tou():
    return render_template('simple/tou.html')


@app.route('/help')
def help():
    return render_template('simple/help.html')


@app.route('/image/<iid>/<size>')
def image(iid, size):
    return img(iid, size)


@app.route('/image/<iid>/<size>/nfit')
def nfimage(iid, size):
    return img(iid, size, False)


@app.route('/message', methods=('POST',))
def message():
    if conf.MESSAGES_BLOCKED:
        abort(410)
    msg = Message.from_request(request)
    try:
        msg.save()
    except ValidationError, e:
        return dumps({'status': 'error', 'message': e.message})
    return dumps({'status': 'ok'})


@app.route('/moderate', methods=('GET', 'POST'))
def moderate():
    if request.method == 'POST':
        msg = Message.objects.with_id(request.values['msgid'])
        msg.delete()
    return render_template(
        'simple/moderate.html',
        messages=paginate(Message.objects.order_by('-date'),
                          conf.MESSAGES_MAX_PERPAGE))


@app.route('/people.json')
def people_json():
    return dumps([msg.to_json() for msg in Message.geolocations])


@app.route('/images.json')
def images_json():
    objs = paginate(Message.slideshow, conf.GALLERY_MAX_PERPAGE)
    objs['collection'] = [x.to_json() for x in objs['collection']]
    return dumps(objs)


@app.route('/messages.json')
def messages_json():
    objs = paginate(Message.objects.order_by('-date'),
                    conf.MESSAGES_MAX_PERPAGE)
    objs['collection'] = [x.to_json() for x in objs['collection']]
    return dumps(objs)


@app.route('/messages/<mid>.json')
def message_json(mid):
    try:
        obj = Message.objects.with_id(mid) or abort(404)
    except ValidationError:
        abort(404)
    return dumps(obj.to_json())


def main():
    """Shortcut to run dad application
    """
    app.run(host=conf.HOST, port=conf.PORT, debug=conf.DEBUG)


if __name__ == '__main__':
    main()
