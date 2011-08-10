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

from flask import Flask, Response, render_template, request
from model import Message
from mongoengine import ValidationError
from json import dumps, loads

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('simple/index.html', Message=Message)


@app.route('/gallery')
def gallery():
    return render_template('simple/gallery.html', Message=Message)


@app.route('/messages')
def messages():
    return render_template('simple/messages.html', Message=Message)


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
    people = []
    for msg in Message.objects:
        if msg.geolocation:
            people.append(loads(
                '{"name":"%s", "thumb":"%s", "latitude":"%s", "longitude":"%s"}' % (
                    msg.sender_name,
                    msg.sender_avatar,
                    msg.geolocation[1],
                    msg.geolocation[0])
             ))

    collection = dumps({"people": people})
    return collection


if __name__ == '__main__':
    app.run(debug=True)
