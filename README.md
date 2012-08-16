# This is the software used to thank Debian

It uses a lot of fun software to work, but unfortunatelly some of them
are not packaged yet. This README file will help you installing them and
the `thank' software itself.

## Dependencies

### Packaged software

 * python-flask
 * python-pyexiv2
 * python-imaging
 * mongodb-server
 * python-mongoengine
 * libjs-jquery
 * libjs-openlayers
 * libjs-jquery-fancybox

### NodeJS Modules (not-packaged)

First of all, I suggest you to install the `npm' package. It will make
it painless to install the following packages:

  * sass (https://github.com/visionmedia/sass.js)
  * clean-css (https://github.com/GoalSmashers/clean-css)

To procced with the installation, just issue the following commands:

    $ npm install sass
    $ npm install clean-css

It will probably complain that your `~/bin` dir is not in your PATH if
you don't have one, but it will not break anything.


## Setting configuration params

### conf.py.sample

After checking out the source code, you have to copy the
`conf.py.sample` to `conf.py`. In this file, you'll be able to choose
the database name that messages and pictures will be stored. If the
already set name (dad) is ok to you, just go ahead.

### Database setup

We're using mongodb in this app. It makes our life really easier. You
don't actually need to change anything to make things happen.

Anyway, it's worth to check if the choosen name will not screw with an
already running service in your computer and we are ready to go!

### Sass Vs. Css: Generating css files

We're not using css directly in this app. All styles are being defined
in the `sass` language. So, before running the app, you have to compile
the sass files, use the following:

    $ scripts/compilecss

If you aim to help the project sending patches, maybe it would be good
to start a watcher that will compile sass files when they change. To do
it, use it:

    $ scripts/compilecss -w

## Actually running the app

Currently, you just have to issue:

    $ python app.py

You'be informed about the host and port being used by the embedded HTTP
server provided by flask, so you can just point your browser to that URL
and hopefully, you will be in front of our work.

## Development:

### Show me the code

To get the source code, please clone it from our temporary git repo:

    $ git clone http://comum.org/~lincoln/imago.git/
