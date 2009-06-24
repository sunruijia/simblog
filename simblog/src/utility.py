# encoding: utf-8

from functools import wraps
from google.appengine.api import users
from google.appengine.api import memcache
from datetime import datetime
import email

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
            memcache.set(key,(result,response.headers['last-modified']),1)
            return      
    return wrapper


class Message:
    def __init__(self,msg_raw):
        msg = email.message_from_string(msg_raw)
        self.data = {}
        self.data["email-date"] = msg["Received"].split(";")[1].strip()
        email_subject = email.Header.decode_header(msg["Subject"])
        if not email_subject:
            self.data["email-subject"] = "Untitled"
        else:
            self.data["email-subject"] = email_subject[0][0].decode(email_subject[0][1])
        self.payload_data = self._get_payload_data(msg)
        self.data["email-text"] = self.payload_data
        
    def _get_payload_data(self, msg):
        if msg.is_multipart():
            payloads = msg.get_payload()
            return self._get_payload_data(payloads[0])
        else:
            payload_data = msg.get_payload(decode=True).decode(msg.get_param('charset'))  
        return payload_data
    
    
    