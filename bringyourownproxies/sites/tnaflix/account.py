# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

__all__ = ['TnaflixAccount']

class TnaflixAccount(_Account):
    
    SITE = 'Tnaflix'
    SITE_URL = 'www.tnaflix.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(TnaflixAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):

        attempt_login  = self._login(extra_post_vars={"remember_me":"on" if self.remember_me else "off",
                                                    "next":"/my_profile.php"},
                                    post_url='https://www.tnaflix.com/getiton.php')

        if attempt_login.url == 'https://www.tnaflix.com/my_profile.php':
            return True
        else:
            doc = self.etree.fromstring(attempt_login.content,self.parser)
                
            get_error_msg = doc.xpath('//div[@class="notificationBlock notifErrorBlock"]//text()')
            
            if get_error_msg:
                error_msg =  "".join([txt for txt in get_error_msg])
                if 'Invalid Username/Password or your account is not verified yet.' in error_msg:
                    raise InvalidLogin('Wrong username or password, or account is not verified')
            
            raise AccountProblem('Unknown problem while login into Tnaflix')

            
    def is_logined(self):
        return self._is_logined(sign_out_xpath='//a[@title="Log Out"]')

