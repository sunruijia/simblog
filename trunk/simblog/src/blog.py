# encoding: utf-8
import wsgiref.handlers
import os
import re
import cgi
import datetime
import sys

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import memcache


import model
from model import Blog
import main

class BasePublicBlog(main.BaseRequestHandler):
    def get(self):
        self.generateBasePage('manage/addblog.html')
        return
    def post(self):
        title1,content1 = (self.request.get(item) for item in ('title', 'content'))
        blogEntity = model.Blog(title = title1, content = content1, createTimeStamp = datetime.datetime.now())
        blogEntity.publish()
        self.redirect('/')

class BlogManager(main.BaseRequestHandler):
    def get(self):
        blogs = Blog.all().order('-createTimeStamp').fetch(10)
        template_values = {
              'blogs': blogs
        }
        self.generateBasePage('manage/blogs.html',template_values)
        return
    def post(self):
        checkedIDs= self.request.get_all('checks')
        for id in checkedIDs:
            keyID = int(id)
            blog = Blog.get_by_id(keyID)
            blog.delete()
        self.redirect('/admin/blogs')
        return
    
def Main():
    application = webapp.WSGIApplication([('/admin/', BasePublicBlog),('/admin/post', BasePublicBlog),
                                          ('/admin/blogs',BlogManager)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
  Main()
