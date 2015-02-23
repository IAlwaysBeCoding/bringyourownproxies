#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class TnaflixAccount(OnlineAccount):
    
    SITE = 'Tnaflix'
    SITE_URL = 'www.tnaflix.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(TnaflixAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_tnaflix = session.get('http://www.tnaflix.com',proxies=proxy)

        post = {"next":"/my_profile.php",
                "username":self.username,
                "password":self.password,
                "remember_me":"on" if self.remember_me else "off"}
        
        attempt_login = session.post('https://www.tnaflix.com/getiton.php',data=post,proxies=proxy)

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
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_Tnaflix = session.get('http://www.Tnaflix.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_Tnaflix.content,self.parser)
        is_sign_out_link = doc.xpath('//a[@href="/logout.php" and @class="logout"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  TnaflixAccount(username='tedwantsmore',password='money1003d',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()