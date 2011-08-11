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

var title_format = function(title, currentArray, currentIndex, currentOpts){
    return '<span id="fancybox-title-over">Image ' +  (currentIndex + 1) +
        ' / ' + currentArray.length + ' ' + title + '</span>';
};

$("a[rel=group]").fancybox({
    'transitionIn'  : 'none',
    'transitionOut' : 'none',
    'titlePosition' : 'over',
    'titleFormat'   : title_format,
    'type' : 'image'
});
