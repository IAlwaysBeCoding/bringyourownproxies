#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class VpornAccount(OnlineAccount):
    
    SITE = 'Vporn'
    SITE_URL = 'www.vporn.com'
    
    def __init__(self,username,password,email,**kwargs):

        super(VpornAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_vporn = session.get('http://www.vporn.com',proxies=proxy)

        post = {"username":self.username,
                "password":self.password,
                "backto": "http://www.vporn.com"}
        

        attempt_login = session.post('http://www.vporn.com/login',data=post,proxies=proxy)

        doc = self.etree.fromstring(attempt_login.content,self.parser)
        
        find_profile_element = doc.xpath('//a[@href="/profile" and @style="display: inline;"]')
        if find_profile_element:
            return True
        else:
            get_error_msg = doc.xpath('//div[@style="color: red;"]')
            if get_error_msg:
                if get_error_msg[0].text == 'Invalid username or password':
                    raise InvalidLogin('Wrong username or password')
                else:
                   raise AccountProblem('Unknown problem while login into' \
                                        'Vporn message:{msg}'.format(msg=get_error_msg[0].text))
            raise AccountProblem('Unknown problem while login into Vporn')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_vporn = session.get('http://www.vporn.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_vporn.content,self.parser)
        is_sign_out_link = doc.xpath('//a[@href="/profile" and @style="display: inline;"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  VpornAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()