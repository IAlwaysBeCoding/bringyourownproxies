# -*- coding: utf-8 -*-
#!/usr/bin/python
import json
import path

from lxml import etree
from lxml.etree import HTMLParser,tostring
from requests.cookies import create_cookie

from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.errors import CookiesFileDoesNotExist
from bringyourownproxies.cookies import CookieLoader

class Account(object):
    def __init__(self,username=None,password=None,**kwargs):
        self.username = username
        self.password = password

class OnlineAccount(Account):
    SITE = 'NOT SPECIFIED'
    SITE_URL = None

    parser = HTMLParser()
    etree = etree
    tostring = tostring
    cookie_loader = CookieLoader()

    def __init__(self,username,password,**kwargs):
        self.username = username
        self.password = password
        self.http_settings = kwargs.pop('http_settings',HttpSettings())
        self.email = kwargs.pop('email',None)
        super(OnlineAccount,self).__init__(username=username,password=password,**kwargs)

    @classmethod
    def create_account(cls,profile,http_settings):
        raise NotImplementedError('''
                                This should return a new Account instance
                                and should take a Profile instance
                                and HttpSettings instance as parameters
                                ''')

    def login(self,**kwargs):
        raise NotImplementedError('Subclasses should implement this')

    def is_logined(self):
        raise NotImplementedError('is_logined needs to be implemented by the subclasses of this class')

    def save_cookies(self,filename):

        cookies_loc = self.http_settings.session.cookies._cookies
        cookies = self.cookie_loader.session_cookies_to_json(cookies_loc=cookies_loc)

        with open(filename,'w+') as f:
            f.write(json.dumps(cookies))

    def load_cookies(self,filename):
        f = path.Path(filename)
        if not f.exists():
            raise CookiesFileDoesNotExist('cookie file:{f} does not exist'.format(f=filename))

        self.cookie_loader.set_cookies_from_json(json_cookies_file=filename,
                                                 session=self.http_settings.session)

