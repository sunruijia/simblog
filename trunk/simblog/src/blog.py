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
from model import blogSystem
import main

class BasePublicBlog(main.BaseRequestHandler):
    def get(self):
        action = self.param('action')
        if(action == ''):
            value ={'action':'?action=add'}
        elif(action=='edit'):
            key = self.param('key')
            blog = Blog.get(key)
            value={'action':'?key='+ key +'&action=edit',
                   'title':blog.title,
                   'content':blog.content} 
        self.generateBasePage('manage/addblog.html',value)
        return
    def post(self):
        key = self.param('key')
        action = self.param('action')
        title1,content1 = (self.request.get(item) for item in ('title', 'content'))
        if(action=='add'):            
            blogEntity = Blog(title = title1, content = content1, createTimeStamp = datetime.datetime.now())
            blogEntity.publish()
            self.redirect('/')
        elif(action=='edit'):
            blogEntity = Blog.get(key)
            blogEntity.title = title1
            blogEntity.content = content1
            blogEntity.put()
            self.redirect('/?p=%d'%blogEntity.blog_id)
        

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

class BlogSystemManager(main.BaseRequestHandler):
    def get(self):
        self.generateBasePage('manage/config.html')      
        return
    def post(self):
        blogSystem.title,blogSystem.subTitle,blogSystem.systemURL,blogSystem.systemDomain = (
            self.request.get(item) for item in ('title', 'subtitle', 'url', 'domain'))
        blogSystem.posts_per_page = int(self.request.get( 'posts_per_page'))
        blogSystem.put()
        self.redirect('/admin/config')
        return
    
        
def Main():
    application = webapp.WSGIApplication([('/admin/', BasePublicBlog),('/admin/post', BasePublicBlog),
                                          ('/admin/blogs',BlogManager),('/admin/config',BlogSystemManager)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
  Main()
