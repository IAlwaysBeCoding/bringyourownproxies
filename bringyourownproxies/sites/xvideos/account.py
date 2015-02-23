#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class XVideosAccount(OnlineAccount):
    
    SITE = 'XVideos'
    SITE_URL = 'www.xvideos.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        
        super(XVideosAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_xvideos = session.get('http://www.xvideos.com',proxies=proxy)
        

        post = {"referer":"http://www.xvideos.com/",
                "login":self.email,
                "password":self.password,
                "rememberme":"on" if self.remember_me else "off",
                "log":"Login to your account"}
                
        attempt_login = session.post('http://upload.xvideos.com/account',data=post,proxies=proxy)
        

        doc = self.etree.fromstring(attempt_login.content,self.parser)

        find_errors = doc.xpath('//p[@class="inlineError form_global_error"]/text()')
        if find_errors:

            if find_errors[0] == 'Bad username or password.':
                raise InvalidLogin('Wrong username or password')
            raise AccountProblem('Unknown problem occured while trying to login into xvideos.com')
        else:
            return True 
            
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
    account =  XVideosAccount(username='tedwantsmore',password='money1003d',email='tedwantsmore@gmx.com')
    account.login()