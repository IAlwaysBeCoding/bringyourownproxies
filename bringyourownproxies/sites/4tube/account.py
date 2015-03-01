#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class _4tubeAccount(OnlineAccount):
    
    SITE = '_4tube'
    SITE_URL = 'www.4tube.com'
    
    def __init__(self,username,password,email,**kwargs):
        super(_4tubeAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_4tube = session.get('http://www.4tube.com',proxies=proxy)
        post = {"_target_path":"/",
                "_username":self.username,
                "_password":self.password}
        
        go_to_login = session.get('http://www.4tube.com/login',proxies=proxy)
        session.headers.update({"X-Requested-With":"XMLHttpRequest",
                                "Accept":"application/json, text/javascript, */*; q=0.01"})
        
        attempt_login = session.post('http://www.4tube.com/login_check',data=post,proxies=proxy)
        response =  attempt_login.json()
        
        if response['result'] == 'ok':
            return True
            
        raise AccountProblem('Something went wrong while login into 4tube.com')
        
    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        go_to_porntube = session.get('http://www.4tube.com/users/{username}/edit'.format(username=self.username),proxies=proxy)

        doc = self.etree.fromstring(go_to_porntube.content,self.parser)
        get_title = doc.xpath('//title')
        if get_title:

            if 'Page not found' in get_title[0].text:
                return False
            else:
                return True
if __name__ == '__main__':
    account =  _4tubeAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()
