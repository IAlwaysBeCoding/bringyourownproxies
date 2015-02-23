#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class TubeCupAccount(OnlineAccount):
    
    SITE = 'TubeCup'
    SITE_URL = 'www.tubecup.com'
    
    def __init__(self,username,password,email,**kwargs):
        
        super(TubeCupAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_tubecup = session.get('http://www.tubecup.com',proxies=proxy)

        post = {"username":self.username,
                "pass":self.password,
                "redirect_to":"http://www.tubecup.com/",
                "action":"login"}
                
        attempt_login = session.post('http://www.tubecup.com/login.php',data=post,proxies=proxy)
        
        doc = self.etree.fromstring(attempt_login.content,self.parser)
        find_error_msg = doc.xpath('//div[@class="message_error"]')
        if find_error_msg:
            if find_error_msg[0].text.strip() == 'Invalid Username or Password. Username and Password are case-sensitive.':
                raise InvalidLogin('Wrong username or password')
        else:

            if doc.xpath('//a[@class="logout"]'):
                return True
        
        raise AccountProblem('Unknown problem while login into TubeCup')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_tubecup = session.get('http://www.tubecup.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_tubecup.content,self.parser)
        is_sign_out_link = doc.xpath('//a[@class="logout"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  TubeCupAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()