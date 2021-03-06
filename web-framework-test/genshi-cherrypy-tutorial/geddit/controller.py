#!/usr/bin/env python

import operator, os, pickle, sys

import cherrypy
from formencode import Invalid
from genshi.filters import HTMLFormFiller


from geddit.form import LinkForm, CommentForm
from geddit.model import Link, Comment
from geddit.lib import template

class Root(object):
    def __init__(self, data):
        self.data = data

    @cherrypy.expose
    @template.output('index.html')
    def index(self):
        links = sorted(self.data.values(), key=operator.attrgetter('time'))
        return template.render(links=links)

    @cherrypy.expose
    @template.output('submit.html')
    def submit(self, cancel=False, **data):
        if cherrypy.request.method == 'POST':
            if cancel:
                raise cherrypy.HTTPRedirect('/')
            # validate the input data!
            form = LinkForm()
            try:
                data = form.to_python(data)
                link = Link(**data)
                self.data[link.id] = link
                raise cherrypy.HTTPRedirect('/')
            except Invalid, e:
                errors = e.unpack_errors()
        else:
            errors = {}
            
        return template.render(errors=errors) | HTMLFormFiller(data=data)

    @cherrypy.expose
    @template.output('info.html')
    def info(self, id):
        link = self.data.get(id)
        if not link:
            raise cherrypy.NotFound()
        return template.render(link=link)

    @cherrypy.expose
    @template.output('comment.html')
    def comment(self, id, cancel=False, **data):
        link = self.data.get(id)
        if not link:
            raise cherrypy.NotFound()
        if cherrypy.request.method == 'POST':
            if cancel:
                raise cherrypy.HTTPRedirect('/info/%s' % link.id)
            form = CommentForm()
            try:
                data = form.to_python(data)
                comment = link.add_comment(**data)
                raise cherrypy.HTTPRedirect('/info/%s' % link.id)
            except Invalid, e:
                errors = e.unpack_errors()
        else:
            errors = {}

        return template.render(link=link, comment=None,
                               errors=errors) | HTMLFormFiller(data=data)


def main(filename):
    # load data from the pickle file, or initialize it to an empty list
    if os.path.exists(filename):
        fileobj = open(filename, 'rb')
        try:
            data = pickle.load(fileobj)
        finally:
            fileobj.close()
    else:
        data = {}

    def _save_data():
        fileobj = open(filename, 'wb')
        try:
            pickle.dump(data, fileobj)
        finally:
            fileobj.close()
            
    if hasattr(cherrypy.engine, 'subscribe'):  # cherrypy >=3.1
        cherrypy.engine.subscribe('stop', _save_data)
    else:
        cherrypy.engine.on_stop_engine_list.append(_save_data)

    # Some global configuration; note that this could be moved into a
    # configuration file
    cherrypy.config.update({
        'tools.encode.on': True, 'tools.encode.encoding': 'utf-8',
        'tools.decode.on': True,
        'tools.trailing_slash.on': True,
        'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
    })

    cherrypy.quickstart(Root(data), '/', {
        '/media': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static'
        }
    })


    
if __name__ == '__main__':
    main(sys.argv[1])

    # $ PYTHONPATH=. python geddit/controller.py geddit.db
