#!/usr/bin/python
import base64

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class YouJizzAccount(OnlineAccount):
    
    SITE = 'YouJizz'
    SITE_URL = 'www.youjizz.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(YouJizzAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_youjizz = session.get('http://www.youjizz.com',proxies=proxy)

        post = {"ahd_username":self.username,
                "ahd_password":base64.b64encode(self.password),
                "Submit":"Login",
                "rememberme":"on" if self.remember_me else "off"}
        
        
        attempt_login = session.post('http://www.youjizz.com/login_auth.php',data=post,proxies=proxy)

        doc = self.etree.fromstring(attempt_login.content,self.parser)
        if doc.xpath('//a[@href="/logout.php"]'):
            return True
        else:
            find_error_p = doc.xpath('//p')
            if find_error_p:
                for p in find_error_p:
                    if p.text.strip() == 'The login information you have provided was incorrect. Please try again.':
                        raise InvalidLogin('Wrong username or password')
        
        raise AccountProblem('Unknown problem while login into YouJizz')


    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_youjizz = session.get('http://www.youjizz.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_youjizz.content,self.parser)
        is_sign_out_link = doc.xpath('//a[@href="/logout.php"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  YouJizzAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()