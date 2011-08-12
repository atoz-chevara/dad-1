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
import Image
from StringIO import StringIO
from mongoengine import connect, Document, StringField, EmailField, \
    ListField, DictField, DateTimeField, GeoPointField, FileField, \
    queryset_manager
from flask import escape, url_for, Markup

import conf

connect(conf.DATABASE_NAME)


PKG_URL_PATTERN = u'<a href="http://packages.debian.org/%(n)s">%(n)s</a>'

TAG_URL_PATTERN = u'<a href="http://identi.ca/tag/%(n)s">#%(n)s</a>'

AVATAR_SIZE = '32'


def build_gravatar(email):
    """Builds a gravatar url to get an avatar to a registered user or
    the default one
    """
    url = "http://www.gravatar.com/avatar/%s?%s&d=mm" % (
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
    get = lambda key:metadata.get(key) and metadata.get(key).value or ''
    data = {
        'longref': get('Exif.GPSInfo.GPSLongitudeRef'),
        'long': get('Exif.GPSInfo.GPSLongitude'),
        'latref': get('Exif.GPSInfo.GPSLatitudeRef'),
        'lat': get('Exif.GPSInfo.GPSLatitude'),
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
        if data['longref'] == 'W':
            longi = -longi

        # Saving the result
        result['geolocation'] = (longi, lat)

    return result


class Message(Document):
    """All metadata stored about the message and the `attached' image is
    present in this model, including info about its sender
    """

    # Sender data
    sender_name = StringField(required=True, min_length=1)
    sender_email = EmailField()
    sender_website = StringField()
    sender_avatar = StringField()
    sender_geolocation = GeoPointField()

    # Message itself and content found inside it through the `#' and `:'
    # symbols.
    content = StringField(required=True, min_length=10)
    packages = ListField(StringField())
    tags = ListField(StringField(max_length=30))

    # General metadata
    date = DateTimeField(default=datetime.now)

    # Image specific fields
    image = FileField()
    thumbs = DictField()
    image_geolocation = GeoPointField()

    @staticmethod
    def from_request(request):
        message = Message()

        # Avoiding dots
        vals = request.values

        # Ensuring that a value will be None if we receive it empty
        val = lambda key:vals.get(key) and vals[key] or None

        # Filling out sender attributes
        message.sender_name = val('name')
        message.sender_email = val('email')
        message.sender_website = val('url')
        message.sender_avatar = val('avatar') or \
            build_gravatar(val('email'))
        if val('latitude') and val('longitude'):
            message.sender_geolocation = (
                float(val('longitude')),
                float(val('latitude')))

        # Finding tags and packages in the message content
        message.content = escape(val('message'))
        message.tags = find_tags(val('message'))
        message.packages = find_packages(vals['message'])

        # Filling out image attribute
        image_data = process_image(val('image'))
        message.image = image_data['image']
        message.image_geolocation = image_data['geolocation']

        return message

    @queryset_manager
    def slideshow(doc_cls, queryset):
        """A queryset manager that lists messages with images and orders
        by date DESC.
        """
        return queryset(__raw__={'$where': 'this.image !== null'})\
            .order_by('-date')

    @queryset_manager
    def geolocations(doc_cls, queryset):
        """A queryset manager that lists only messages with geolocation
        information.
        """
        return queryset(__raw__={
                '$where': 'this.sender_geolocation !== null || \
                           this.image_geolocation !== null'})

    @property
    def has_image(self):
        """Returns a boolean value saying if we have an image or not in
        the message.
        """
        return self.image.grid_id is not None

    @property
    def formatted_username(self):
        """Returns the username collected in the message sending
        form. If none was informed, the `Anonymous' string is
        returned."""
        return self.sender_name or u'Anonymous'

    @property
    def formatted_content(self):
        """Returns the content separated in paragraphs. The string that
        creates a new paragraph is the '\n'.
        """
        content = self.content
        for i in self.tags:
            tag = u'#%s' % i
            content = content.replace(tag, TAG_URL_PATTERN % {'n': i})

        for i in self.packages:
            pkg = u':%s' % i
            content = content.replace(pkg, PKG_URL_PATTERN % {'n': i})

        paragraphs = [(u'<p>%s</p>' % i) for i in content.split('\n')]
        return Markup(u'\n'.join(paragraphs))

    @property
    def geolocation(self):
        """This method decides the best data to be used as coordinates
        to be shown on the map. The priority list is sender and then
        image info.
        """
        return self.sender_geolocation or self.image_geolocation or None

    def thumb(self, size):
        """Returns a cached thumbnail (depending on the size). If it
        does not exist, _gen_thumb() is called to deliver the image.
        """
        return self.thumbs.get('%dx%d' % size, self._gen_thumb(size))

    def _gen_thumb(self, size):
        """Generates a thumbnail (and caches it) based on the internal
        `image' attribute.
        """
        output = StringIO()
        img = Image.open(StringIO(self.image.read()))
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(output, 'PNG')
        self.thumbs['%dx%d' % size] = output.getvalue()
        return self.thumbs['%dx%d' % size]

    def to_json(self):
        """Returns a JSON representation of the object
        """
        base = self.to_mongo().copy()
        for key in '_cls', '_id', '_types', 'image', 'thumbs', 'sender_email':
            # `sender_email' is not required, so it could be missing!
            try:
                del base[key]
            except KeyError:
                continue

        # Readding some important fields that needed to be converted
        # before being added to a JSON object.
        base['id'] = str(self.id)
        base['date'] = base['date'].isoformat()

        # Adding geolocation info to both sender and image
        base['image_longitude'] = self.image_geolocation and \
            self.image_geolocation[0]
        base['image_latitude'] = self.image_geolocation and \
            self.image_geolocation[1]
        base['sender_longitude'] = self.sender_geolocation and \
            self.sender_geolocation[0]
        base['sender_latitude'] = self.sender_geolocation and \
            self.sender_geolocation[1]

        # Adding image info
        base['image_url'] = url_for('image', iid=self.id, size='800x600')
        base['thumb_url'] = url_for('image', iid=self.id, size='80x80')
        return base
