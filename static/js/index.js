/* Copyright (C) 2011  Lincoln de Sousa <lincoln@comum.org>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

(function() {
    $('form#thanks').submit(function(evt) {
        var form, params;
        evt.preventDefault();
        form = $(this);
        params = {
            type: 'post',
            url: form.attr('action'),
            dataType: 'json',
            data: {
                name: $('#name').val(),
                email: $('#email').val(),
                url: $('#url').val(),
                avatar: $('#avatar').val(),
                message: $('#message').val(),
                image: $('#image').val(),
                team: $('#team').val()
            },
            success: function(data) {
                if (data.status === 'error') {
                    $('.successMsg').hide();
                    $('.errMsg pre').html(data.message);
                    $('.errMsg').show();
                    return setTimeout(function() {
                        return $('.errMsg').hide(400);
                    }, 5000);
                } else {
                    $('.errMsg').hide();
                    $('.successMsg').show();
                    form[0].reset();
                    return setTimeout(function() {
                        return $('.successMsg').hide(400);
                    }, 5000);
                }
            }
        };
        $.ajax(params);
        return false;
    });

    /* Fancybox for slideshow */
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

    /* Setting up `identi.ca' box */
    $('#identica_search').liveTwitter(
        '#thxdebian',
        {service: 'identi.ca', limit: 5, rate: 5000});

}).call(this);
