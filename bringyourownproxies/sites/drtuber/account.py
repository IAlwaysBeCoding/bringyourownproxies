#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

__all__ = ['DrTuberAccount']

class DrTuberAccount(_Account):
    
    SITE = 'DrTuber'
    SITE_URL = 'www.drTuber.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(DrTuberAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):

        attempt_login  = self._login(extra_post_vars={
                                                    'submit_login':'true',
                                                    'login_remember':'true' if self.remember_me else 'false'
                                                    },
                                    ajax=True,
                                    before_post_url='http://www.drtuber.com/ajax/popup_forms?form=login',
                                    post_url='http://www.drtuber.com/ajax/login')
        
        result = attempt_login.json() 

        if result['success']:
            return True
        else:
            if result['error'] == 'Invalid username and/or password!':
                raise InvalidLogin('Wrong username or password')
        raise AccountProblem('Unknown problem while login into DrTuber message:{e}'.format(e=result['error']))

        
    def is_logined(self):
        return self._is_logined(sign_out_xpath='//a[@href="/logout"]')

