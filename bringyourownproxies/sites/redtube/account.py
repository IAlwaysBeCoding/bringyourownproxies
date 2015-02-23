#!/usr/bin/python
import re
import json

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class RedTubeAccount(OnlineAccount):
    
    SITE = 'RedTube'
    SITE_URL = 'www.redtube.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        
        super(RedTubeAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_RedTube = session.get('http://www.redtube.com',proxies=proxy)
        

        post = {"iFriendID":0,
                "iObjectID":0,
                "iObjectType":0,
                "sUsername":self.username,
                "sPassword":self.password,
                "bRemember":"2" if self.remember_me else "1",
                "do":"Log in"}
        session.headers.update({"X-Requested-With":"XMLHttpRequest"})
        attempt_login = session.post('http://www.redtube.com/htmllogin',data=post,proxies=proxy)
        is_success = re.findall(r'parent.loginSuccess\((.*?)\);',attempt_login.content,re.I|re.M)

        if is_success:
            try:
                response = json.loads(is_success[0])
            except:
                raise AccountProblem('Could not read json login response')
            print response['success']
            if response['success']:
                return True

        else:
            doc = self.etree.fromstring(attempt_login.content,self.parser)
            find_errors = doc.xpath('//p[@class="error-summary"]/text()')
            if find_errors:
                if find_errors[0] == 'Username or password incorrect. Please try again.':
                    raise InvalidLogin('Wrong username or password')
            
        raise AccountProblem('Unknown error while trying to loging into redtube.com')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_redtube = session.get('http://www.redtube.com/community',proxies=proxy)

        doc = self.etree.fromstring(go_to_redtube.content,self.parser)
        find_all_a = doc.xpath('//a[@href="javascript:;" and @onclick]')
        found_login_a = False
        for a in find_all_a:

            if 'showLogin()' in a.attrib['onclick']:
                found_login_a = True
                break
        if found_login_a:
            return False
        else:
            return True

if __name__ == '__main__':
    account =  RedTubeAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()