#!/usr/bin/python

from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.httpclient import HttpSettings
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
        self.http_settings = kwargs.pop('http_settings') if kwargs.get('http_settings',False) else HttpSettings()
        self.email = kwargs.pop('email') if kwargs.get('email',False) else None
        super(OnlineAccount,self).__init__(username=username,password=password,**kwargs)

    @classmethod
    def create_account(cls,profile,http_settings):
        raise NotImplementedError('''
                                This should return a new Account instance 
                                and should take a Profile instance
                                and HttpSettings instance as parameters
                                ''')
    
    def login(self):
        raise NotImplementedError('login method needs to be implemented from classes subclassing from this class')

    