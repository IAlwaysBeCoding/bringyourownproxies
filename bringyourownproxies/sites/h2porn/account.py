#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class H2PornAccount(OnlineAccount):
    
    SITE = 'H2Porn'
    SITE_URL = 'www.H2Porn.com'
    
    def __init__(self,username,password,email,**kwargs):
        super(H2PornAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_H2Porn = session.get('http://www.H2Porn.com',proxies=proxy)
        post = {"action":"login",
                "redirect_to":"http://H2Porn.com/",
                "username":self.username,
                "pass":self.password}
        

        attempt_login = session.post('http://H2Porn.com/login.php',data=post,proxies=proxy)
        doc = self.etree.fromstring(attempt_login.content,self.parser)

        if doc.xpath('//li[@class="logout"]'):
            return True
        else:
            get_error_msg = doc.xpath('//div[@class="message_error"]')
            
            if get_error_msg[0].text.strip() == 'Invalid Username or Password. Username and Password are case-sensitive.':
                raise InvalidLogin('Wrong username or password')    
            else:
                raise AccountProblem('Unknown problem while login into' \
                                'H2Porn message:{msg}'.format(msg=get_error_msg[0].text.strip()))

            raise AccountProblem('Unknown problem while login into H2Porn')
        
    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_H2Porn = session.get('http://www.H2Porn.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_H2Porn.content,self.parser)
        is_sign_out_link = doc.xpath('//li[@class="logout"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  H2PornAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()