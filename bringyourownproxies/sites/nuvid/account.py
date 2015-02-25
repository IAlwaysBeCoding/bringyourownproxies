#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class NuvidAccount(OnlineAccount):
    
    SITE = 'Nuvid'
    SITE_URL = 'www.nuvid.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(NuvidAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_nuvid = session.get('http://www.nuvid.com',proxies=proxy)

        post = {"username":self.username,
                "password":self.password,
                "login_remember": "1" if self.remember_me else "0",
                "submit_login":"true"}

        session.headers.update({"X-Requested-With":"XMLHttpRequest"})
        attempt_login = session.post('http://www.nuvid.com/ajax/login',data=post,proxies=proxy)

        result = attempt_login.json()

        if result['success']:
            return True
        else:
            if result['error'] == 'Invalid username and/or password!':
                raise InvalidLogin('Wrong username or password')
            else:
                raise AccountProblem('Unknown problem while login into' \
                                    'Nuvid message:{msg}'.format(msg=result['error']))
        raise AccountProblem('Unknown problem while login into Nuvid')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_nuvid = session.get('http://www.nuvid.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_nuvid.content,self.parser)
        is_sign_out_link = doc.xpath('//a[@class="l1" and @href="/logout"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  NuvidAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()
