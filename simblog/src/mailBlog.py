# -*- coding: utf-8 -*- 

import os
import cgi
import wsgiref.handlers


from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from utility import  *
from main import *

import model
from model import Blog
from model import blogSystem

class check_mail(BaseRequestHandler):
    def post(self):
        sender = self.request.GET.get("from", "")
        if sender == blogSystem.postEmailAddr:
            msg = Message(self.request.body)
            blogEntity = Blog(title = msg.data["email-subject"], content = msg.data["email-text"], createTimeStamp = datetime.now())
            blogEntity.publish()              
        return

def Main():
    application = webapp.WSGIApplication([('/check_mail', check_mail)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
  Main()
    
    