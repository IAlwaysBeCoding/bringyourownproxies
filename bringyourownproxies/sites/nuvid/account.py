# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account

__all__ = ['NuvidAccount']

class NuvidAccount(_Account):

    SITE = 'Nuvid'
    SITE_URL = 'www.nuvid.com'

    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(NuvidAccount,self).__init__(username=username,password=password,email=email,**kwargs)

    def login(self):

        attempt_login  = self._login(extra_post_vars = {
                                                        "login_remember": "1" if self.remember_me else "0",
                                                        "submit_login":"true"},
                                    ajax=True,
                                    post_url='http://www.nuvid.com/ajax/login')


        result = attempt_login.json()

        if result['success']:
            return True
        else:
            if result['error'] == 'Invalid username and/or password!':
                raise InvalidLogin('Wrong username or password')
            else:
                raise AccountProblem('Unknown problem while login into' \
                                    'Nuvid message:{msg}'.format(msg=result['error']))
        raise AccountProblem('Unknown problem while login into Nuvid')
    def is_logined(self):
        return self._is_logined(sign_out_xpath='//a[@class="l1" and @href="/logout"]')


