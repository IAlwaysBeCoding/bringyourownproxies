#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class PornTubeAccount(OnlineAccount):
    
    SITE = 'PornTube'
    SITE_URL = 'www.porntube.com'
    
    def __init__(self,username,password,email,**kwargs):
        super(PornTubeAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_porntube = session.get('http://www.porntube.com',proxies=proxy)

        post = {"_username":self.username,
                "_password":self.password,
                "_target_path": "/"}
                
        go_to_login = session.get('http://www.porntube.com/login',proxies=proxy)
        session.headers.update({"X-Requested-With":"XMLHttpRequest",
                                "Accept":"application/json, text/javascript, */*; q=0.01"})
        attempt_login = session.post('http://www.porntube.com/login_check',data=post,proxies=proxy)

        check_logined = self.is_logined()
        if check_logined:
            return True
        else:
            raise AccountProblem('Unknown problem while login into PornTube')
            
    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        go_to_porntube = session.get('http://www.porntube.com/users/{username}/edit'.format(username=self.username),proxies=proxy)

        doc = self.etree.fromstring(go_to_porntube.content,self.parser)
        get_title = doc.xpath('//title')
        if get_title:

            if 'Page not found' in get_title[0].text:
                return False
            else:
                return True

if __name__ == '__main__':
    account =  PornTubeAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()
