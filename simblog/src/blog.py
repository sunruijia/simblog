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
from model import Comment
from model import  Link

import main
from utility import  *

class BasePublicBlog(main.BaseRequestHandler):
    @checkAdmin
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
    @checkAdmin
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

    @checkAdmin
    def get(self):
        blogs = Blog.all().order('-createTimeStamp').fetch(10)
        template_values = {
              'blogs': blogs
        }
        self.generateBasePage('manage/blogs.html',template_values)
        return
    @checkAdmin
    def post(self):
        checkedIDs= self.request.get_all('checks')
        for id in checkedIDs:
            keyID = int(id)
            blog = Blog.get_by_id(keyID)
            blog.delete()
        self.redirect('/admin/blogs')
        return

class BlogSystemManager(main.BaseRequestHandler):

    @checkAdmin
    def get(self):
        self.generateBasePage('manage/config.html')      
        return
    @checkAdmin
    def post(self):
        blogSystem.title,blogSystem.subTitle,blogSystem.systemURL,blogSystem.systemDomain,blogSystem.feedURL = (
            self.request.get(item) for item in ('title', 'subtitle', 'url', 'domain','feed_url'))
        blogSystem.posts_per_page = int(self.request.get( 'posts_per_page'))
        blogSystem.put()
        self.redirect('/admin/config')
        return
    
class BlogCommentManager(main.BaseRequestHandler):
    @checkAdmin
    def get(self):
        comments=Comment.all().order('-commentTime')
        values = {'comments':comments}
        self.generateBasePage('manage/comments.html', values)
        return
    
    @checkAdmin
    def post(self):
        try:
            checkList = self.request.get_all('checks')
            for key in checkList:
                keyID = int(key)
                comment=Comment.get_by_id(keyID)
                comment.delete()
        finally:
            self.redirect('/admin/comments')
        return
    
class BlogLinksManager(main.BaseRequestHandler):
    @checkAdmin
    def get(self):
        links = Link.all()
        values = {'links':links}
        self.generateBasePage('manage/links.html', values)
        return
    
    @checkAdmin
    def post(self):
        try:
            checkList = self.request.get_all('checks')
            for key in checkList:
                keyID = int(key)
                link=Link.get_by_id(keyID)
                link.delete()
        finally:
            self.redirect('/admin/links')        
        return   
 
class BlogLinkManager(main.BaseRequestHandler):
    @checkAdmin
    def get(self):
        action = self.param('action')
        values = {'action':action}
        if(action == 'edit'):
            key = self.param('id')
            link = Link.get_by_id(int(key))
            values.update({'link':link})
        self.generateBasePage('manage/link.html', values)
        return
    @checkAdmin
    def post(self):
        action = self.param('action')
        name,url = (self.request.get(item) for item in ('linkName', 'linkURL'))
        if(action == 'edit'):
            key = self.param('id')
            link = Link.get_by_id(int(key))
            link.linkName = name
            link.linkURL = url
        else:
            link = Link(linkName=name,linkURL=url)
        link.put()
        self.redirect('/admin/links')   
        return  
               
def Main():
    application = webapp.WSGIApplication([('/admin/', BasePublicBlog),('/admin/post', BasePublicBlog),
                                          ('/admin/blogs',BlogManager),('/admin/config',BlogSystemManager),
                                          ('/admin/comments',BlogCommentManager),
                                          ('/admin/links',BlogLinksManager),
                                          ('/admin/link',BlogLinkManager)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
  Main()
