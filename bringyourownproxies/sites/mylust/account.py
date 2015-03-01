#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

class MyLustAccount(_Account):
    
    SITE = 'MyLust'
    SITE_URL = 'www.mylust.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(MyLustAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):

        attempt_login  = self._login(password='pass',
                                    extra_post_vars={"action":"login"},
                                    post_url='http://mylust.com/login.php')
        
        self._find_login_errors(response=attempt_login,
                                error_msg_xpath='//div[@class="message_error"]/text()',
                                wrong_pass_msg='Invalid Username or Password. Username and Password are case-sensitive.')


    def is_logined(self):
        return self._is_logined(sign_out_xpath='//i[@class="fa fa-sign-out"]')

if __name__ == '__main__':
    account =  MyLustAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()