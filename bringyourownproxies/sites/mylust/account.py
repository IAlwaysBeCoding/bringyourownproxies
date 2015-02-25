#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class MyLustAccount(OnlineAccount):
    
    SITE = 'MyLust'
    SITE_URL = 'www.mylust.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(MyLustAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_mylust = session.get('http://www.mylust.com',proxies=proxy)

        go_to_login = session.get('http://mylust.com/login.php',proxies=proxy)
        
        post = {"action":"login",
                "username":self.username,
                "pass":self.password}
        

        attempt_login = session.post('http://mylust.com/login.php',data=post,proxies=proxy)
        doc = self.etree.fromstring(attempt_login.content,self.parser)

        if doc.xpath('//i[@class="fa fa-sign-out"]'):
            return True
        else:
            get_error_msg = doc.xpath('//div[@class="message_error"]')
            if get_error_msg:
                if get_error_msg[0].text.strip() == 'Invalid Username or Password. Username and Password are case-sensitive.':
                    raise InvalidLogin('Wrong username or password')
                else:
                    raise AccountProblem('Unknown problem while login into' \
                                    'MyLust message:{msg}'.format(msg=get_error_msg[0].text.strip()))

            raise AccountProblem('Unknown problem while login into MyLust')
        
    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_mylust = session.get('http://www.mylust.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_mylust.content,self.parser)
        is_sign_out_link = doc.xpath('//i[@class="fa fa-sign-out"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  MyLustAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()