#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class MotherlessAccount(OnlineAccount):
    
    SITE = 'Motherless'
    SITE_URL = 'www.Motherless.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(MotherlessAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_motherless = session.get('http://www.motherless.com',proxies=proxy)

    
        post = {"botcheck":"no bots!",
                "username":self.username,
                "password":self.password,
                "__remember_me":"1" if self.remember_me else "0"}
        
        attempt_login = session.post('https://motherless.com/login',data=post,proxies=proxy)

        if 'var __logged_in = true;' in attempt_login.content:
            return True
        else:
            doc = self.etree.fromstring(attempt_login.content,self.parser)
                
            get_error_msg = doc.xpath('//div[@class="flash-message error"]')
            found_wrong_pass_msg = False
            
            for error_msg in get_error_msg:
                if error_msg.text.strip() == 'Incorrect username or password.':
                    found_wrong_pass_msg = True
                    break
            
            if found_wrong_pass_msg:
                raise InvalidLogin('Wrong username or password')
            else:
                raise AccountProblem('Unknown problem while login into Motherless')

            
    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_motherless = session.get('http://www.motherless.com/',proxies=proxy)
        
        if 'var __logged_in = true;' in go_to_motherless.content:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  MotherlessAccount(username='trythis1003',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()