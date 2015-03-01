#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

class FreepornvsAccount(_Account):
    
    SITE = 'Freepornvs'
    SITE_URL = 'www.freepornvs.com'
    
    def __init__(self,username,password,email,**kwargs):
        super(FreepornvsAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        attempt_login  = self._login(password='pass',
                                    extra_post_vars={'action':'login'},
                                    post_url='http://freepornvs.com/sign-in/',
                                    before_post_url='http://freepornvs.com/sign-in/')


        self._find_login_errors(attempt_login)

            
    def is_logined(self):
        return self._is_logined(sign_out_xpath='//a[@href="/sign-out/"]')
        
if __name__ == '__main__':
    account =  FreepornvsAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()