#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

__all__ = ['FuxAccount']

class FuxAccount(_Account):
    
    SITE = 'Fux'
    SITE_URL = 'www.fux.com'
    
    def __init__(self,username,password,email,**kwargs):
        super(FuxAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        attempt_login  = self._login(username='_username',
                                    password='_password',
                                    extra_post_vars={"_target_path":"/"},
                                    ajax=True,
                                    before_post_url='http://www.fux.com/login',
                                    post_url='http://www.fux.com/login_check')

        response =  attempt_login.json()
        
        if response['result'] == 'ok':
            return True

        raise AccountProblem('Something went wrong while login into 4tube.com')
        
    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        go_to_fux = session.get('http://www.fux.com/user/{username}/edit'.format(username=self.username),proxies=proxy)
        
        doc = self.etree.fromstring(go_to_fux.content,self.parser)
        get_title = doc.xpath('//title')
        if get_title:
            if 'Page not found' in get_title[0].text:
                return False
            else:
                return True

