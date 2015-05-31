# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
import json
import path

from lxml import etree
from lxml.etree import HTMLParser,tostring
from requests.cookies import create_cookie

from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.errors import CookiesFileDoesNotExist

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

    def _put_cookies_in_a_dict(self,cookies_loc):

        cookies = {}
        for domain in cookies_loc:
            if not domain in cookies:
                cookies[domain] = {}

            for path in cookies_loc[domain]:
                if not path in cookies[domain]:
                    cookies[domain][path] = {}

                for cookie in cookies_loc[domain][path]:
                    cookies[domain][path][cookie] = cookies_loc[domain][path][cookie].value

        return cookies

    def save_cookies(self,filename):

        cookies_loc = self.http_settings.session.cookies._cookies
        cookies = self._put_cookies_in_a_dict(cookies_loc=cookies_loc)

        with open(filename,'w+') as f:
            f.write(json.dumps(cookies))

    def load_cookies(self,filename):
        f = path.Path(filename)
        if not f.exists():
            raise CookiesFileDoesNotExist('cookie file:{f} does not exist'.format(f=filename))

        with open(filename,'r') as f:
            data = f.read()

        cookies_loc = self.http_settings.session.cookies._cookies
        cookies = self._put_cookies_in_a_dict(cookies_loc=cookies_loc)

        raw_cookies = json.loads(data)

        for raw_cookies_domain in raw_cookies:
            if not raw_cookies_domain in cookies_loc:
                cookies_loc[raw_cookies_domain] = {}

            for raw_cookies_path in raw_cookies[raw_cookies_domain]:
                if not raw_cookies_path in cookies_loc[raw_cookies_domain]:
                    cookies_loc[raw_cookies_domain][raw_cookies_path] = {}

                for raw_cookie in raw_cookies[raw_cookies_domain][raw_cookies_path]:
                    if not raw_cookie in cookies_loc[raw_cookies_domain][raw_cookies_path]:
                        new_cookie = create_cookie(raw_cookie,
                                                    raw_cookies[raw_cookies_domain][raw_cookies_path][raw_cookie])
                        cookies_loc[raw_cookies_domain][raw_cookies_path][raw_cookie] = new_cookie


