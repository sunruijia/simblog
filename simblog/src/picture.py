# encoding: utf-8
import os
import cgi
import wsgiref.handlers

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import images


from model import Blog
from model import Link
from model import blogSystem
from model import Comment
from model import Picture
from utility import  *
from main import *

class SinglePicManager(BaseRequestHandler):
    @checkAdmin
    def get(self):
        action = self.param('action')
        values = {'action':action}
        if(action == 'edit'):
             key = self.param('id')
             pic = Picture.get_by_id(int(key))
             values.update({'pic':pic})
        self.generateBasePage('manage/pic.html', values)      

    @checkAdmin
    def post(self):
        action = self.param('action')
        picName = self.request.get('picName')
        if(action == 'add'):
            picContent = self.request.get('pic')
            pic = Picture()
            pic.picName = picName
            if(picContent != None):
                pic.picContent = db.Blob(picContent)
                pic.thumbnail = db.Blob(images.resize(picContent,128,128))
            pic.put()
            pic.picLink = '/picture/show?img_id=%s&amp;type=full'%pic.key().id()
            pic.put()
        elif(action == 'edit'):
             key = self.param('id')
             pic = Picture.get_by_id(int(key))
             pic.picName = picName
             pic.put()
        self.redirect('/picture')
        
class PicsManager(BaseRequestHandler):
    @checkAdmin
    def get(self):
        pics = Picture.all()
        values = {'pics':pics}
        self.generateBasePage('manage/pics.html', values)
        return
    
    @checkAdmin
    def post(self):
        try:
            checkList = self.request.get_all('checks')
            for key in checkList:
                keyID = int(key)
                pic = Picture.get_by_id(keyID)
                pic.delete()
        finally:
            self.redirect('/picture')  
        return        
        
class ShowPic(BaseRequestHandler):
    def get(self):
        type = self.param('type')
        key = self.param('img_id')
        keyID = int(key)
        pic = Picture.get_by_id(keyID)
        if(pic):
            if(type == 'thumb'):
                content = pic.thumbnail
            else:
                content = pic.picContent
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(content)
        else:
            self.response.out.write("No image")
            
        return

        
def Main():
    application = webapp.WSGIApplication([('/picture/upload', SinglePicManager),
                                          ('/picture', PicsManager),('/picture/show', ShowPic)], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == '__main__':
  Main()            