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

from datetime import datetime
from mongoengine import connect, Document, StringField, EmailField, \
    ReferenceField, ListField, DateTimeField, GeoPointField, FileField


connect('imago')


class User(Document):
    name = StringField()
    email = EmailField(required=True)
    password = StringField(required=True)
    friends = ListField(ReferenceField('User'))

    def __unicode__(self):
        return self.name


class Image(Document):
    title = StringField()
    description = StringField()
    tags = ListField(StringField(max_length=30))
    date = DateTimeField(default=datetime.now)
    geolocation = GeoPointField()
    image = FileField(required=True)
