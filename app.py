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

from flask import Flask, Response, render_template, request, abort
from model import Message
from mongoengine import ValidationError
from json import dumps, loads
import conf

app = Flask(__name__)


def paginate():
    page = int(request.values.get('p', 1))-1
    maxperpage = conf.GALLERY_MAX_PERPAGE
    return maxperpage * page, (maxperpage*page) + maxperpage

@app.route('/')
def index():
    return render_template('simple/index.html', Message=Message)


@app.route('/gallery')
def gallery():
    skip, limit = paginate()
    return render_template('simple/gallery.html', slideshow=Message.slideshow[skip:limit])


@app.route('/messages')
def messages():
    return render_template('simple/messages.html', Message=Message)


@app.route('/about')
def about():
    return render_template('simple/about.html')


@app.route('/help')
def help():
    return render_template('simple/help.html')


@app.route('/image/<iid>/<size>/')
def image(iid, size):
    size = tuple(int(x) for x in size.split('x'))
    return Response(
        Message.objects.with_id(iid).thumb(size),
        content_type='image/png')


@app.route('/message', methods=('POST',))
def message():
    msg = Message.from_request(request)
    try:
        msg.save()
    except ValidationError, e:
        return dumps({'status': 'error', 'message': e.message})
    return dumps({'status': 'ok'})


@app.route('/people.json')
def people_json():
    return dumps([msg.to_json() for msg in Message.geolocations])


@app.route('/images.json')
def images_json():
    skip, limit = paginate()
    return dumps([m.to_json() for m in Message.slideshow[skip:limit]])


@app.route('/messages.json')
def messages_json():
    skip, limit = paginate()
    objs = Message.objects[skip:limit].order_by('-date')
    return dumps([m.to_json() for m in objs])


@app.route('/messages/<mid>.json')
def message_json(mid):
    try:
        obj = Message.objects.with_id(mid) or abort(404)
    except ValidationError:
        abort(404)
    return dumps(obj.to_json())


if __name__ == '__main__':
    app.run(host=conf.HOST, port=conf.PORT, debug=conf.DEBUG)
