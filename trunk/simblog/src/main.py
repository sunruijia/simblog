# encoding: utf-8
import os
import cgi
import wsgiref.handlers

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from model import Blog
from model import blogSystem

class BaseRequestHandler(webapp.RequestHandler):
    def generateBasePage(self,template_name,values={}):
        self.init()
        template_values = {
            'self':self,                           
           'blogSystem':blogSystem
            }
        template_values.update(values)
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, os.path.join('templates', template_name))
        html = template.render(path, template_values)
        self.response.out.write(html)
   
    def param(self, name, **kw):
        return self.request.get(name, **kw)
    def init(self):
        self.loginURL = users.create_login_url(self.request.uri)
        self.logoutURL = users.create_logout_url(self.request.uri)
        self.login_user = users.get_current_user()
        self.isLogin = (self.login_user!=None)
        self.isAdmin = users.is_current_user_admin()
        
        return

class MainPageHandler(BaseRequestHandler):
    def get(self):
        blogid=self.param('p')
        if(blogid):
            blogid=int(blogid)
            blogs = Blog.all().filter('blog_id =', blogid).fetch(1)
            blog= blogs[0]
            template_values = {'blog':blog, 'blogsystem':blogSystem}
            self.generateBasePage('singleblog.html', template_values)
        else:
            pageIndex = self.param('page')
            if (pageIndex):
                pageIndex = int(pageIndex)
            else:
                pageIndex = 1;
            blogs = Blog.all().order('-createTimeStamp')    
            pager = PageManager(query=blogs,items_per_page=blogSystem.posts_per_page)
            blogs,links = pager.fetch(pageIndex)
            template_values = {
              'blogs': blogs,
              'pager': links
             }
            self.generateBasePage('main.html',template_values)
        return

class singleBlog(BaseRequestHandler):
    def get(self,blogid=None):

        return

class PageManager(object):
    def __init__(self, model=None,query=None, items_per_page=10):
        if model:
            self.query = model.all()
        elif query:
            self.query=query

        self.items_per_page = items_per_page

    def fetch(self, p):
        max_offset = self.query.count()
        n = max_offset / self.items_per_page
        if max_offset % self.items_per_page != 0:
            n += 1
        if p < 0 or p > n:
            p = 1
        offset = (p - 1) * self.items_per_page
        results = self.query.fetch(self.items_per_page, offset)
        links = {'count':max_offset,'page_index':p,'prev': p - 1, 'next': p + 1, 'last': n}
        if links['next'] > n:
            links['next'] = 0
        return (results, links)
    

def Main():
    application = webapp.WSGIApplication([('/', MainPageHandler)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    return

if __name__ == "__main__":
    Main()