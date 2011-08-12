/**
    Copyright (C) 2011 Marcelo Jorge Vieira <metal@alucinados.com>

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public
    License along with this program; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place - Suite 330,
    Boston, MA 02111-1307, USA.
*/

var initial_lon = -1800244.88985;
var initial_lat = 1878516.4068;
var initial_zoom = 2;
var zoom_levels = 20;
var projection = new OpenLayers.Projection("EPSG:900913");
var display_projection = new OpenLayers.Projection("EPSG:4326");

function map_init() {
    var map = new OpenLayers.Map (
        'map', {
            controls: [
                new OpenLayers.Control.Navigation(),
                new OpenLayers.Control.PanZoomBar(),
                new OpenLayers.Control.ScaleLine(),
                new OpenLayers.Control.Permalink('Permalink'),
                new OpenLayers.Control.MousePosition()
            ],
            numZoomLevels: zoom_levels
        });

    // OSM layer
    var osm = new OpenLayers.Layer.OSM ("Open Street Map");
    map.addLayer(osm);

    var display_photos = function (response) {
        /* Parsing data */
        var json = new OpenLayers.Format.JSON();
        var data = json.read(response.responseText);

        /* Adding the marker */
        var markers = new OpenLayers.Layer.Markers("People");
        map.addLayer(markers);

        /* Icon size and position */
        var size = new OpenLayers.Size(20, 20);
        var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);

        /* Time to insert people on the map */
        for (var x in data) {
            var icon = new OpenLayers.Icon(data[x].sender_avatar, size, offset);
            var location = new OpenLayers.LonLat(
                data[x].sender_longitude,
                data[x].sender_latitude);
            var transform = location.transform(display_projection, projection);
            var marker = new OpenLayers.Marker(transform, icon);
            var display_popup = function (evt) {
                alert( data[x].sender_name );
                OpenLayers.Event.stop(evt);
            };
            marker.events.register('mousedown', marker, display_popup);
            markers.addMarker(marker);
        }
    };

    var url = "/people.json";
    var parameters = {};
    OpenLayers.loadURL(url, parameters, this, display_photos);

    // Initial position
    var initial_location = new OpenLayers.LonLat(initial_lon,initial_lat);
    var initial_transform = initial_location.transform(
        display_projection,
        projection);
    map.setCenter(initial_transform, initial_zoom);
}

$().ready(function () {
    map_init();
});
