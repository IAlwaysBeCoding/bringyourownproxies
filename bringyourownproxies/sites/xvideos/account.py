#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

class XVideosAccount(_Account):
    
    SITE = 'XVideos'
    SITE_URL = 'www.xvideos.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        
        super(XVideosAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        attempt_login  = self._login(use_username=False,
                                    extra_post_vars={"referer":"http://www.xvideos.com/",
                                                    "login":self.email,
                                                    "rememberme":"on" if self.remember_me else "off",
                                                    "log":"Login to your account"},
                                    post_url='http://upload.xvideos.com/account')

        self._find_login_errors(response=attempt_login,
                                error_msg_xpath='//p[@class="inlineError form_global_error"]/text()',
                                wrong_pass_msg='Bad username or password.'
                                )

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_sex = session.get('http://upload.xvideos.com/account',proxies=proxy)
        doc = self.etree.fromstring(go_to_sex.content,self.parser)

        if doc.xpath('//form[@id="signinForm"]'):
            return False
        else:
            return True

if __name__ == '__main__':
    account =  XVideosAccount(username='tedwantsmored',password='money1003dsdss',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()