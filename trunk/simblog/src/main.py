# encoding: utf-8
import os
import cgi
import wsgiref.handlers

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class BaseRequestHandler(webapp.RequestHandler):
    def generateBasePage(self,template_name,values={}):
        template_values = {            
            'request': self.request,
            'user': users.GetCurrentUser(),
            'login_url': users.CreateLoginURL(self.request.uri),
            'logout_url': users.CreateLogoutURL('http://' + self.request.host + '/'),
            'blog_link': 'http://' + self.request.host + '/'}
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, os.path.join('templates', template_name))
        html = template.render(path, values)
        self.response.out.write(html)
        return

class MainPageHandler(BaseRequestHandler):
    def get(self):
        self.generateBasePage('main.html')
        return



def Main():
    application = webapp.WSGIApplication([(r'/(\d+)$', MainPageHandler),('/', MainPageHandler)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    return

if __name__ == "__main__":
    Main()