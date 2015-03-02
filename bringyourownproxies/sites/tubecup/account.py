#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

class TubeCupAccount(_Account):
    
    SITE = 'TubeCup'
    SITE_URL = 'www.tubecup.com'
    
    def __init__(self,username,password,email,**kwargs):
        
        super(TubeCupAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):

        attempt_login  = self._login(password='pass',
                                    extra_post_vars={'action':'login','redirect_to':'http://voyeurhit.com'},
                                    post_url='http://www.tubecup.com/login.php')

        self._find_login_errors(attempt_login,
                                error_msg_xpath='//div[@class="message_error"]/text()',
                                wrong_pass_msg='Invalid Username or Password. Username and Password are case-sensitive.')

    def is_logined(self):
        return self._is_logined(sign_out_xpath='//a[@class="logout"]')
if __name__ == '__main__':
    account =  TubeCupAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()