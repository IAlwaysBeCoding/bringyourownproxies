#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class SexAccount(OnlineAccount):
    
    SITE = 'SEX'
    SITE_URL = 'www.sex.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        
        super(SexAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_sex = session.get('http://www.sex.com',proxies=proxy)
        
        post = {"email":self.email,
                "password":self.password,
                "remember":"true" if self.remember_me else "false",
                "submit":"Sign In"}
                
        attempt_login = session.post('http://www.sex.com/user/signin?redirect=%2F',data=post,proxies=proxy)
        

        doc = self.etree.fromstring(attempt_login.content,self.parser)
        if doc.xpath('//a[@href="/user/signout"]'):
            return True
        else:
            get_error = doc.xpath('//div[@id="error"]/text()')
            if get_error:
                if get_error[0] == 'Wrong email or password':
                    raise InvalidLogin('Wrong email or password, could not log into Sex.com')
            
            raise AccountProblem('Unknown problem, could not log into sex.com')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_sex = session.get('http://www.sex.com',proxies=proxy)
        doc = self.etree.fromstring(go_to_sex.content,self.parser)
        if doc.xpath('//a[@href="/user/signout"]'):
            return True
        else:
            return False

if __name__ == '__main__':
    account = SexAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()