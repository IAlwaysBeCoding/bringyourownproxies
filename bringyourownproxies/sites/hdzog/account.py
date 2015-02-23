#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class HdZogAccount(OnlineAccount):
    
    SITE = 'HdZog'
    SITE_URL = 'www.hdzog.com'
    
    def __init__(self,username,password,email,**kwargs):
       super(HdZogAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_hdzog = session.get('http://www.hdzog.com',proxies=proxy)

        post = {"action":"login",
                "username":self.username,
                "pass":self.password,
                "redirect_to": "http://www.hdzog.com"}
        

        attempt_login = session.post('http://www.hdzog.com/login.php',data=post,proxies=proxy)

        doc = self.etree.fromstring(attempt_login.content,self.parser)
        
        if doc.xpath('//a[@class="logout" and @title="Logout"]'):
            return True
        else:
            get_error_msg = doc.xpath('//div[@class="message-block message-error"]/p')
            if get_error_msg:
                if get_error_msg[0].text == 'Invalid Username or Password. Username and Password are case-sensitive.':
                    raise InvalidLogin('Wrong username or password')
        raise AccountProblem('Unknown problem while login into HdZog')


    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_hdzog = session.get('http://www.hdzog.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_hdzog.content,self.parser)
        is_sign_out_link = doc.xpath('//a[@class="logout" and @title="Logout"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  HdZogAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()