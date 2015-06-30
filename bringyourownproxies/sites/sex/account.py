# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account

__all__ = ['SexAccount']

class SexAccount(_Account):

    SITE = 'SEX'
    SITE_URL = 'www.sex.com'

    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(SexAccount,self).__init__(username=username,password=password,email=email,**kwargs)

    def login(self):

        attempt_login  = self._login(extra_post_vars={"remember":"true" if self.remember_me else "false",
                                                    "submit":"Sign In",
                                                    "email":self.email},
                                    use_username=False,
                                    post_url='http://www.sex.com/user/signin?redirect=%2F')

        self._find_login_errors(response=attempt_login,
                                error_msg_xpath='//div[@id="error"]/text()',
                                wrong_pass_msg='Wrong email or password'
                                )
    def is_logined(self):
        return self._is_logined(sign_out_xpath='//a[@href="/user/signout"]')

if __name__ == '__main__':
    from bringyourownproxies.sites import SexAccount
