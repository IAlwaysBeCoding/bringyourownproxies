# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

__all__ = ['Tube8Account']

class Tube8Account(_Account):
    
    SITE = 'Tube8'
    SITE_URL = 'www.tube8.com'
    
    def __init__(self,username,password,email,**kwargs):
        
        super(Tube8Account,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):

        attempt_login  = self._login(ajax=True,
                                    post_url='http://www.tube8.com/ajax2/login/')

        result = attempt_login.json()
        if int(result['statusCode']) == 1:
            return True
        else:
            if result['message'] == 'Invalid login credentials':
                raise InvalidLogin('Wrong username or password')
            raise AccountProblem('Unknown problem while login into tube8 message:{m}'.format(m=result['message']))
        raise AccountProblem('Unknown problem while login into tube8')


    def is_logined(self):
        return self._is_logined(sign_out_xpath='//a[@class="logout-button"]')

