# -*- coding: utf-8 -*-
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
            cookies[domain] = cookies.get(domain,{})

            for path in cookies_loc[domain]:
                cookies[domain][path] = cookies[domain].get(path,{})

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

        r_cookies = json.loads(data)

        for r_c_domain in r_cookies:
            cookies_loc.get(r_c_domain,{})

            for r_c_path in r_cookies[r_c_domain]:
                cookies_loc[r_c_domain][r_c_path] = cookies_loc[r_c_domain].get(r_c_path,{})
                for raw_cookie in r_cookies[r_c_domain][r_c_path]:
                    new_cookie = create_cookie(raw_cookie,
                                            r_cookies[r_c_domain][r_c_path][raw_cookie])
                    cookies_loc[r_c_domain][r_c_path][raw_cookie] = new_cookie


