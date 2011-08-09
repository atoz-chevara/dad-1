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

"""This module holds the definition of the schema used to store data in
mongodb
"""

import re
from hashlib import md5
from urllib import urlencode, urlopen
from datetime import datetime
from pyexiv2 import ImageMetadata
from mongoengine import connect, Document, StringField, EmailField, \
    ListField, DateTimeField, GeoPointField, FileField


connect('dad')


def build_gravatar(email):
    """Builds a gravatar url to get an avatar to a registered user or
    the default one
    """
    url = "http://www.gravatar.com/avatar/%s?%s" % (
        email and md5(email.lower()).hexdigest() or '',
        urlencode({ 's': AVATAR_SIZE }))
    return url


TAG_REGEXP = re.compile('\#([\w\-]+)')

def find_tags(content):
    """Finds words prefixed with a hashtag `#' symbol
    """
    return TAG_REGEXP.findall(content)


PKG_REGEXP = re.compile('\:([\w\-]+)')

def find_packages(content):
    """Finds words prefixed with a hashtag `#' symbol
    """
    return PKG_REGEXP.findall(content)


def process_image(url):
    """Tries to get an image from a given url and extract its
    geolocation metadata.
    """
    result = {'image': None, 'geolocation': None }
    if not url:
        return result

    # First, let's try to get the image
    flike = urlopen(url)
    if flike.getcode() != 200:
        # Not found
        return result

    if not flike.headers.get('content-type', '').startswith('image/'):
        # Not an image
        return result

    result['image'] = flike.read()
    metadata = ImageMetadata.from_buffer(result['image'])
    metadata.read()

    # Geolocation stuff
    data = {
        'longref': metadata.get('Exif.GPSInfo.GPSLongitudeRef').value,
        'long': metadata.get('Exif.GPSInfo.GPSLongitude').value,
        'latref': metadata.get('Exif.GPSInfo.GPSLatitudeRef').value,
        'lat': metadata.get('Exif.GPSInfo.GPSLatitude').value,
    }

    # If one single key is missing, we can't process it
    if data.values() == [i for i in data.values() if i]:
        # Yes, we got geolocation info. Let's parse it. To understand
        # it, refer to the exiv2 doc: http://www.exiv2.org/tags.html

        lat = data['lat']
        lat = float(lat[0] + lat[1] / 60 + lat[2] / 3600)
        if data['latref'] == 'S':
            lat = -lat

        longi = data['long']
        longi = float(longi[0] + longi[1] / 60 + longi[2] / 3600)
        if data['longref'] == 'S':
            longi = -longi

        # Saving the result
        result['geolocation'] = (lat, longi)

    return result


class Message(Document):
    """All metadata stored about the message and the `attached' image is
    present in this model, including info about its sender
    """

    # Sender data
    sender_name = StringField(required=True)
    sender_email = EmailField()
    sender_website = StringField()
    sender_avatar = StringField()

    # Message itself and content found inside it through the `#' and `:'
    # symbols.
    content = StringField()
    packages = ListField(StringField())
    tags = ListField(StringField(max_length=30))

    # General metadata
    date = DateTimeField(default=datetime.now)

    # Image specific fields
    image = FileField()
    geolocation = GeoPointField()

    @staticmethod
    def from_request(request):
        message = Message()

        # Avoiding dots
        vals = request.values

        # Filling out sender attributes
        message.sender_name = vals['name']
        message.sender_email = vals['email']
        message.sender_website = vals['url']
        message.sender_avatar = vals['avatar'] or \
            build_gravatar(vals['email'])

        # Finding tags and packages in the message content
        message.tags = find_tags(vals['message'])
        message.packages = find_packages(vals['message'])

        # Filling out image attribute
        image_data = process_image(vals['image'])
        message.image = image_data['image']
        message.geolocation = image_data['geolocation']

        return message
