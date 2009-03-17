# encoding: utf-8
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

blogSystem = None

class Blog(db.Model):
    author = db.UserProperty()
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    createTimeStamp = db.DateTimeProperty(required=True)
    selfLink = db.StringProperty(multiline=False,default='')
    blog_id = db.IntegerProperty()
    commentCount = db.IntegerProperty(default=0)
    def save(self):
        return
    def publish(self):
        self.put()
        self.blog_id = self.key().id()
        self.selfLink = '?p=%d'%self.blog_id
        self.put()
    def delete(self):
        comments = Comment.all().filter("ownerBlog =",self)
        if comments:
            for comment in comments:
                comment.delete()
        db.delete(self)
        

class BlogSystem(db.Model):
    owner = db.UserProperty()
    author=db.StringProperty(default='admin')
    title = db.StringProperty(multiline=False)
    subTitle = db.StringProperty(multiline=False)
    systemURL = db.StringProperty(multiline=False)
    systemDomain = db.StringProperty(multiline=False)
    feedURL = db.StringProperty(multiline=False)
    posts_per_page= db.IntegerProperty(default=10)

class Comment(db.Model):
    ownerBlog = db.ReferenceProperty(Blog)
    commentTime = db.DateTimeProperty(auto_now_add=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty()
    authorEmail = db.StringProperty(multiline=False,default='')
    authorURL = db.StringProperty(multiline=False,default='')
    
    @property
    def briefContent(self,len=20):
        return self.content[:len]
    
    def save(self):
        self.put()
        self.ownerBlog.commentCount+=1
        self.ownerBlog.put()
        return
    def delete(self):
        self.ownerBlog.commentCount-=1
        self.ownerBlog.put()
        db.delete(self)

class Link(db.Model):
    linkName = db.StringProperty(multiline=False,default='')
    linkURL = db.StringProperty(multiline=False,default='')

class Picture(db.Model):
    picContent = db.BlobProperty()
    picName = db.StringProperty(multiline=False,default='')
    picLink = db.StringProperty(multiline=False,default='')
    thumbnail = db.BlobProperty()

def initBlogSystemData():
    global blogSystem
    blogSystem = BlogSystem(key_name = 'simblog')
    blogSystem.title = 'Your blog title'
    blogSystem.systemURL = "http://" + os.environ['HTTP_HOST']
    blogSystem.systemDomain = os.environ['HTTP_HOST']
    blogSystem.feedURL = blogSystem.systemURL + "/feed"
    blogSystem.put()
    
def createBlogSystem():
    global blogSystem
    blogSystem = BlogSystem.get_by_key_name('simblog')
    if not blogSystem:
        initBlogSystemData()

createBlogSystem()
    