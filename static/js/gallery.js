/**
    Copyright (C) 2011 Marcelo Jorge Vieira <metal@alucinados.com>
    Copyright (C) 2011 Lincoln de Sousa <lincoln@comum.org>

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

function formatTitle(title, currentArray, currentIndex, currentOpts) {
    var data = $(currentArray[currentIndex]).data('msg');
    var content = [];
    content.push('<span id="fancybox-title-over">');
    content.push('Image by <strong>' + data.sender_name + '</strong> ');
    content.push('&mdash; ' + (currentIndex + 1) + ' / ' + currentArray.length);
    content.push('</span>');
    return content.join('');
}

function initFancyBox() {
    $("a.group").attr({ rel: 'group' }).fancybox({
        'transitionIn'  : 'none',
        'transitionOut' : 'none',
        'titlePosition' : 'over',
        'titleFormat'   : formatTitle,
        'type' : 'image'
    });
}

function setupSlideshow(numImgs) {
    var page = location.hash.replace(/\#/, '') || '1';
    var $ul = $('#slideshow');
    var $nav = $('#nav');
    var url = '../images.json';

    if (numImgs !== undefined) {
        url += '?max=' + numImgs;
    }

    $ul.html('');
    $.getJSON(url, { p: page }, function (data) {
        $(data.collection).each(function (index, msg) {
            var $el = $(tmpl('galleryItemTmpl', msg));
            $('a', $el).data('msg', msg);
            $el.appendTo($ul);
        });

        /* --- Setting up nav commands -- */
        /* Calculating bettter marging position for arrows */
        var marginTop = data.collection.length / 6 * 70;

        $('li.current em', $nav).html('#' + page + '/' + data.pagecount);
        $('li.next, li.prev', $nav).css('margin-top', marginTop + 'px');
        $('li.prev', $nav).html('');
        if (data.previous)
            $('li.prev', $nav).append(
                $('<a>')
                    .html('Previous Page')
                    .attr('href', '#' + data.previous));
        $('li.next', $nav).html('');
        if (data.next)
            $('li.next', $nav).append(
                $('<a>')
                    .html('Next Page')
                    .attr('href', '#' + data.next));

        initFancyBox();
    });
}

$(window).hashchange(function () {
    setupSlideshow();
});
