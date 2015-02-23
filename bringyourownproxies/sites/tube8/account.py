#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class Tube8Account(OnlineAccount):
    
    SITE = 'Tube8'
    SITE_URL = 'www.tube8.com'
    
    def __init__(self,username,password,email,**kwargs):
        
        super(Tube8Account,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_tube8 = session.get('http://www.tube8.com',proxies=proxy)

        post = {"username":self.username,
                "password":self.password}
        
        session.headers.update({"X-Requested-With":"XMLHttpRequest"})
        attempt_login = session.post('http://www.tube8.com/ajax2/login/',data=post,proxies=proxy)

        result = attempt_login.json()
        if int(result['statusCode']) == 1:
            return True
        else:
            if result['message'] == 'Invalid login credentials':
                raise InvalidLogin('Wrong username or password')
            raise AccountProblem('Unknown problem while login into tube8 message:{m}'.format(m=result['message']))
        raise AccountProblem('Unknown problem while login into tube8')


    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_tube8 = session.get('http://www.tube8.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_tube8.content,self.parser)
        is_sign_out_link = doc.xpath('//a[@class="logout-button"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  Tube8Account(username='tedwantsmore',password='money1003d',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()