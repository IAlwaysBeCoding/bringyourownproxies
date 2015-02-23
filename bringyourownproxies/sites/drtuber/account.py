#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class DrTuberAccount(OnlineAccount):
    
    SITE = 'DrTuber'
    SITE_URL = 'www.drTuber.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(DrTuberAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_drtuber = session.get('http://www.drtuber.com',proxies=proxy)

        pop_up_login_form = session.get('http://www.drtuber.com/ajax/popup_forms?form=login',proxies=proxy)
        
        post = {"username":self.username,
                "password":self.password,
                "submit_login":"true",
                "login_remember":"true" if self.remember_me else "false"}
                
        session.headers.update({"X-Requested-With":"XMLHttpRequest"})  
        attempt_login = session.post('http://www.drtuber.com/ajax/login',data=post,proxies=proxy)

        result = attempt_login.json() 

        if result['success']:
            return True
        else:
            if result['error'] == 'Invalid username and/or password!':
                raise InvalidLogin('Wrong username or password')
        raise AccountProblem('Unknown problem while login into DrTuber message:{e}'.format(e=result['error']))

        
    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_DrTuber = session.get('http://www.DrTuber.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_DrTuber.content,self.parser)
        is_sign_out_link = doc.xpath('//a[@href="/logout.php" and @class="logout"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  DrTuberAccount(username='tedwantsmore',password='money1003d',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()