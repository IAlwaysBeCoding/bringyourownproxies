#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class HardSexTubeAccount(OnlineAccount):
    
    SITE = 'HardSexTube'
    SITE_URL = 'www.hardsextube.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(HardSexTubeAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_hardsextube = session.get('http://www.hardsextube.com',proxies=proxy)

        post = {"username":self.username,
                "password":self.password,
                "remember_me": "1" if self.remember_me else "0"}
        
        session.headers.update({"X-Requested-With":"XMLHttpRequest"})
        attempt_login = session.post('http://www.hardsextube.com/login',data=post,proxies=proxy)
        result = attempt_login.json()
        
        if result['success']:
            return True
        else:
            if result['errorMessage'] == 'Username or password is incorrect':
                raise InvalidLogin('Wrong username or password')
            else:
                raise AccountProblem('Unknown problem while login into' \
                                    'Hardsextube message:{msg}'.format(msg=result['errorMessage']))
        raise AccountProblem('Unknown problem while login into Hardsextube')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_hardsextube = session.get('http://www.hardsextube.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_hardsextube.content,self.parser)
        is_sign_out_link = doc.xpath('//i[@class="icon icon-logout"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  HardSexTubeAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()