# encoding: utf-8
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

blogSystem = None

class Blog(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    createTimeStamp = db.DateTimeProperty(required=True)
    selfLink = db.StringProperty(multiline=False,default='')
    blog_id = db.IntegerProperty()
    def save(self):
        return
    def publish(self):
        self.put()
        self.blog_id = self.key().id()
        self.selfLink = '?p=%d'%self.blog_id
        self.put()

class BlogSystem(db.Model):
    title = db.StringProperty(multiline=False)
    subTitle = db.StringProperty(multiline=False)
    systemURL = db.StringProperty(multiline=False)
    systemDomain = db.StringProperty(multiline=False)
    posts_per_page= db.IntegerProperty(default=10)

def initBlogSystemData():
    global blogSystem
    blogSystem = BlogSystem(key_name = 'simblog')
    blogSystem.title = 'Your blog title'
    blogSystem.systemURL = "http://" + os.environ['HTTP_HOST']
    blogSystem.systemDomain = os.environ['HTTP_HOST']
    blogSystem.put()
    
def createBlogSystem():
    global blogSystem
    blogSystem = BlogSystem.get_by_key_name('simblog')
    if not blogSystem:
        initBlogSystemData()

createBlogSystem()
    