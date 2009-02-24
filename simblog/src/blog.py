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
import main

class BasePublicBlog(main.BaseRequestHandler):
    def get(self):
        self.generateBasePage('addblog.html')
        return
    def post(self):
        title1,content1 = (self.request.get(item) for item in ('title', 'content'))
        blogEntity = model.Blog(title = title1, content = content1, createTimeStamp = datetime.datetime.now())
        blogEntity.put()
        self.redirect('/')

def Main():
    application = webapp.WSGIApplication([('/admin/', BasePublicBlog),('/admin/add', BasePublicBlog)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
  Main()
