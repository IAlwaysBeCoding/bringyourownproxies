#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class PrivateHomeClipsAccount(OnlineAccount):
    
    SITE = 'PrivateHomeClips'
    SITE_URL = 'www.PrivateHomeClips.com'
    
    def __init__(self,username,password,email,**kwargs):
        super(PrivateHomeClipsAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_privatehomeclips = session.get('http://www.privatehomeclips.com',proxies=proxy)

        post = {"action":"login",
                "redirect_to":"http://www.privatehomeclips.com/soffer.php",
                "username":self.username,
                "pass":self.password}
        
        attempt_login = session.post('http://www.privatehomeclips.com/login.php',data=post,proxies=proxy)
        
        doc = self.etree.fromstring(attempt_login.content,self.parser)

        if doc.xpath('//a[@href="/logout.php" and @class="logout"]'):
            return True
        else:
            get_error_msg = doc.xpath('//div[@class="message_error"]')
            if get_error_msg:
                if get_error_msg[0].text.strip() == 'Invalid Username or Password. Username and Password are case-sensitive.':
                    raise InvalidLogin('Wrong username or password')
            
            raise AccountProblem('Unknown problem while login into privatehomeclips')


    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_privateHomeClips = session.get('http://www.privatehomeclips.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_PrivateHomeClips.content,self.parser)
        is_sign_out_link = doc.xpath('//a[@href="/logout.php" and @class="logout"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  PrivateHomeClipsAccount(username='tedwantsmore',password='money1003d',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()