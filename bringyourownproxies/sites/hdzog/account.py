# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account

__all__ = ['HdZogAccount']

class HdZogAccount(_Account):

    SITE = 'HdZog'
    SITE_URL = 'www.hdzog.com'

    def __init__(self,username,password,email,**kwargs):
       super(HdZogAccount,self).__init__(username=username,password=password,email=email,**kwargs)

    def login(self):

        attempt_login  = self._login(password='pass',
                                    extra_post_vars={"redirect_to": "http://www.hdzog.com",
                                                    "action":"login"},
                                    post_url='http://www.hdzog.com/login.php')

        self._find_login_errors(response=attempt_login,
                                error_msg_xpath='//div[@class="message-block message-error"]/p',
                                wrong_pass_msg='Invalid Username or Password. Username and Password are case-sensitive.')

    def is_logined(self):
        return self._is_logined(sign_out_xpath='//a[@class="logout" and @title="Logout"]')

