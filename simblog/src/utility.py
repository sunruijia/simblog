# encoding: utf-8

from functools import wraps
from google.appengine.api import users

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