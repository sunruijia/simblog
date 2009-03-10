# encoding: utf-8

from functools import wraps
from google.appengine.api import users
from google.appengine.api import memcache
from datetime import datetime

def checkAdmin(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.isLogin:
            self.redirect(users.create_login_url(self.request.uri))
            return
        elif not self.isAdmin:
            return self.error(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper

def cache(method):
    @wraps(method)
    def wrapper(self,*args,**kwargs):
        request = self.request
        response = self.response
        key = request.url
        html= memcache.get(key)
        if html:
            response.headers['last-modified'] = html[1]
            response.out.write(html[0])
            return
        else:
            response.headers['last-modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
            method(self, *args, **kwargs)
            result=response.out.getvalue()
            memcache.set(key,(result,response.headers['last-modified']),15)
            return      
    return wrapper