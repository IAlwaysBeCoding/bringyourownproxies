#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin,ParsingProblem
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

__all__ = ['PornHubAccount']

class PornHubAccount(_Account):
    
    SITE = 'PornHub'
    SITE_URL = 'www.pornhub.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        
        super(PornHubAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):

        attempt_login  = self._login(extra_post_vars = {"loginPage":1,
                                                        "redirectTo":"",
                                                        "remember_me": "on" if self.remember_me else "off",
                                                        "submit_login":"true"},
                                    ajax=True,
                                    before_post_url='http://www.pornhub.com/login',
                                    before_post_url_vars={"login_key":None,"login_hash":None},
                                    post_url='http://www.pornhub.com/front/login_json')

        response = attempt_login.json()

        if int(response['success']) == 1:
            return True
        else:
            if response['message'] == 'Invalid username/password!':
                raise InvalidLogin('Wrong username or password')
            else:
                raise AccountProblem('Unknown problem while login into Pornhub message:{m}'.format(m=response['message']))
        
        raise AccountProblem('Unknown problem while login into Pornhub')

    def is_logined(self):
        return self._is_logined(sign_out_xpath='//li[@class="signOut"]')

