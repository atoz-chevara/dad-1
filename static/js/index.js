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
        evt.preventDefault();
        var form = $(this);
        var data = {};

        $(this.elements).each(function (key, val) {
            var $field = $(val);
            var name = $field.attr('name');
            if (name !== undefined) {
                data[name] = $field.val();
            }
        });
        var params = {
            type: 'post',
            url: form.attr('action'),
            dataType: 'json',
            data: data,
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


    /* Setting up user avatar url after filling email (gravatar) or
     * avatar url  */
    var defaultGravatar = 'http://www.gravatar.com/avatar/?s=48&d=mm';
    $('#email').change(function () {
        if ($('#avatar').val() === '' &&
            $('#email').val() === '' &&
            $('#gravatar').val() !== defaultGravatar) {
            /* Let's set the default avatar coming from gravatar if, and
             * only if, the user has changed it */
            $('#gravatar').attr('src', defaultGravatar);
        } else if ($('#avatar').val() === '') {
            /* Using gravatar's `API' to get an url for the user's
             * avatar */
            var url = "http://www.gravatar.com/avatar/" +
                    $.md5($(this).val()) +
                    '?s=48&d=mm';
            $('#gravatar').attr('src', url);
        }
    });

    $('#avatar').change(function () {
        var val = $(this).val();
        if (val !== '') {
            $('#gravatar').attr('src', val);
        } else {
            $('#email').change();
        }
    });
}).call(this);
