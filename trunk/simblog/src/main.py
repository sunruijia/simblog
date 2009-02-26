# encoding: utf-8
import os
import cgi
import wsgiref.handlers

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import model
from model import Blog

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
    def param(self, name, **kw):
        return self.request.get(name, **kw)

class MainPageHandler(BaseRequestHandler):
    def get(self):
        blogid=self.param('p')
        if(blogid):
            blogid=int(blogid)
            blogs = Blog.all().filter('blog_id =', blogid).fetch(1)
            blog= blogs[0]
            template_values = {'blog':blog, 'blogsystem':model.blogSystem}
            self.generateBasePage('singleblog.html', template_values)
        else:
            query = Blog.all().order('-createTimeStamp')
            blogs = query.fetch(10)
            template_values = {
              'blogs': blogs
             }
            self.generateBasePage('main.html',template_values)
        return

class singleBlog(BaseRequestHandler):
    def get(self,blogid=None):

        return


def Main():
    application = webapp.WSGIApplication([('/', MainPageHandler)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    return

if __name__ == "__main__":
    Main()