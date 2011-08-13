/* -*- Mode: js2 -*-
 * Copyright (C) 2011  Lincoln de Sousa <lincoln@comum.org>
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


var fs = require('fs'),
    path = require('path'),
    sass = require('sass'),
    cleancss = require('clean-css');


/**
 * Parses a file that holds definitions about which resources this
 * program should manage.
 *
 * @param {String} filePath is the path of the file to be processed.
 * @param {Function} next is a callback to be executed when the file is
 *  finally ready. It receives the JSON object loaded and parsed.
 */
function parseDefinitionFile(filePath, next) {
    fs.readFile(filePath, function (err, data) {
        if (err) {
            throw err;
        } else {
            next(JSON.parse(data));
        }
    });
}


/**
 * This function convert sass files to css, minify css and group files
 *
 * @param {String} base is the base directory of css (or sass) files
 *
 * @param {Array} files is a list of css files that should be grouped
 *  together
 */
function groupCssFiles(base, files) {
    var group = [];
    files.forEach(function (name) {
        var filePath, content;
        if (/\.css$/.test(name)) {
            filePath = path.normalize(path.resolve(base, name));
            content = String(fs.readFileSync(filePath));
        } else {
            filePath = path.normalize(path.resolve(base, name + '.sass'));
            content = sass.render(String(fs.readFileSync(filePath)));
        }
        group.push(cleancss.process(content));
    });
    return group.join('');
}


/**
 * A generic function to call different resource processors
 */
function processResources(ext, resources, processor) {
    var generic = resources.__all__;
    var base = resources.__base__ || '.';
    for (var key in resources) {
        if (key !== '__all__' && key !== '__base__') {
            var files = resources[key];
            if (generic instanceof Array) {
                files = generic.concat(files);
            }
            if (files.length > 0) {
                var name = '_' + key + '.' + ext;
                fs.writeFile(
                    path.resolve(path.join(base, name)),
                    processor(base, files));
            }
        }
    }
}


function main(resources) {
    processResources('css', resources.css, groupCssFiles);
}


if (module == require.main) {
    parseDefinitionFile('resources.json', main);
}
