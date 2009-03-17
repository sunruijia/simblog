# -*- coding: utf-8 -*- 

import os
import cgi
import wsgiref.handlers

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from model import Blog
from model import Link
from model import blogSystem
from model import Comment
from utility import  *
from django.utils import simplejson

class BaseRequestHandler(webapp.RequestHandler):
    def generateBasePage(self,template_name,values={},error=0):
        self.template_values.update(values)
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, os.path.join('templates', template_name))
        html = template.render(path, self.template_values)
        if error != 0:
            self.response.set_status(error)
        self.response.out.write(html)
   
    def param(self, name, **kw):
        return self.request.get(name, **kw)
    
    def initialize(self, request, response):
        webapp.RequestHandler.initialize(self, request, response)
        self.blog = blogSystem
        self.loginURL = users.create_login_url(self.request.uri)
        self.logoutURL = users.create_logout_url(self.request.uri)
        self.login_user = users.get_current_user()
        self.isLogin = (self.login_user!=None)
        self.isAdmin = users.is_current_user_admin()
        self.template_values = {
            'self':self,                           
           'blogSystem':blogSystem
            }
    def error(self,errorCode,msg=''):
        if errorCode == 404:
            message = 'Sorry, we were not able to find the requested page. '
        elif errorCode == 403:
            message = 'Sorry, that page is reserved for administrators.  '
        elif errorCode == 500:
            message = "Sorry, the server encountered an error. "
        else:
            message = msg
        values = {'errorcode':errorCode,'message':message} 
        self.generateBasePage('error.html', values,error=errorCode) 

class MainPageHandler(BaseRequestHandler):
    @cache
    def get(self):
        recentComments = Comment.all().order('-commentTime').fetch(10)
        recentBlogs = Blog.all().order('-createTimeStamp').fetch(5)
        links = Link.all()
        template_values = {'recentComments':recentComments,'recentBlogs':recentBlogs,'links':links}
        blogid=self.param('p')
        if(blogid):
            blogid=int(blogid)
            blogs = Blog.all().filter('blog_id =', blogid).fetch(1)
            blog= blogs[0]   
            comments = Comment.all().filter("ownerBlog =",blog).order('commentTime')
            template_values.update({'blog':blog,'comments':comments})
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
            template_values.update({
              'blogs': blogs,
              'pager': links
             })
            self.generateBasePage('main.html',template_values)
        return

class PostCommentHandler(BaseRequestHandler):
    def post(self):
        if(self.isAdmin):
            name = self.blog.author
            email = self.login_user.email()
            url = self.blog.systemURL
        else:
            name=self.param('author')
            email=self.param('email')
            url=self.param('url')
        key=self.param('key') 
        content=self.param('comment')
        if (name and content):
            ##should be removed when deploy to real site
            content = content.decode('utf8')
            name = name.decode('utf8')
             ##should be removed when deploy to real site
            comment=Comment(author=name,
                            content=content,
                            authorEmail=email,
                            authorURL=url,
                            ownerBlog=Blog.get(key))
            comment.save()
            date = comment.commentTime.strftime("%Y-%m-%d");
            time = comment.commentTime.strftime("%H:%M");
            commentData = {'author':comment.author,'id':comment.key().id(),'url':comment.authorURL,'date':date,'time':time}
            self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
            
            self.response.out.write(simplejson.dumps(commentData))
           # self.redirect(Blog.get(key).selfLink)
        else:
            self.error(501,'Please input name and comment .')
    
    
    
class singleBlog(BaseRequestHandler):
    def get(self,blogid=None):

        return

class RSSHandler(BaseRequestHandler):
    @cache
    def get(self):
        blogs = Blog.all().order('-createTimeStamp').fetch(10)
        if blogs and blogs[0]:
            lastUpdateTime = blogs[0].createTimeStamp
            lastUpdateTime = lastUpdateTime.strftime("%Y-%m-%dT%H:%M:%SZ")
        for blog in blogs:
            blog.formatDate =  blog.createTimeStamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.response.headers['Content-Type'] = 'application/atom+xml'
        values = {'blogs':blogs,'lastUpdateTime':lastUpdateTime}
        self.generateBasePage('atom.xml',values)
        

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
    application = webapp.WSGIApplication([('/', MainPageHandler),('/post_comment',PostCommentHandler),
                                          ('/feed',RSSHandler)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    return

if __name__ == "__main__":
    Main()