# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account

__all__ = ['MotherlessAccount']

class MotherlessAccount(_Account):

    SITE = 'Motherless'
    SITE_URL = 'www.motherless.com'

    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(MotherlessAccount,self).__init__(username=username,password=password,email=email,**kwargs)

    def login(self):

        remember = {}
        if self.remember_me:
            remember['remember_me'] = '1'

        remember['__remember_me'] = '0'

        extra_post_vars = {"botcheck":"no bots!"}
        extra_post_vars.update(remember)

        attempt_login  = self._login(extra_post_vars=extra_post_vars,
                                    post_url='https://motherless.com/login')


        self._find_login_errors(response=attempt_login,
                                wrong_pass_msg ='Incorrect username or password.',
                                error_msg_xpath = '//div[@class="flash-message error"]')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        go_to_motherless = session.get('http://www.motherless.com/',proxies=proxy)

        if 'var __logged_in = true;' in go_to_motherless.content:
            return True
        else:
            return False
