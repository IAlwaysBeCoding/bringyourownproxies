#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin,ParsingProblem
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

class PornHubAccount(_Account):
    
    SITE = 'PornHub'
    SITE_URL = 'www.pornhub.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        
        super(PornHubAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_pornhub = session.get('http://www.pornhub.com',proxies=proxy)
        go_to_pornhub_login = session.get('http://www.pornhub.com/login',proxies=proxy)
        
        doc = self.etree.fromstring(go_to_pornhub_login.content,self.parser)
        get_login_key = doc.xpath('//input[@name="login_key"]')
        if get_login_key:
            login_key = get_login_key[0].attrib['value']
        else:
            raise ParsingProblem('Could not find login_key')

        get_login_hash = doc.xpath('//input[@name="login_hash"]')
        if get_login_hash:
            login_hash = get_login_hash[0].attrib['value']
        else:
            raise ParsingProblem('Could not find login_hash')

        post = {"username":self.username,
                "password":self.password,
                "redirectTo":"",
                "loginPage":1,
                "login_key":login_key,
                "login_hash":login_hash,
                "remember_me":"on" if self.remember_me else "off"}
        session.headers.update({"X-Requested-With":"XMLHttpRequest"})
        attempt_login = session.post('http://www.pornhub.com/front/login_json',data=post,proxies=proxy)
        attempt_login  = self._login(extra_post_vars = {
                                                        "login_remember": "1" if self.remember_me else "0",
                                                        "submit_login":"true"},
                                    ajax=True,
                                    before_post_url='http://www.pornhub.com/login',
                                    before_post_url_vars
                                    post_url='http://www.nuvid.com/ajax/login')

        response = attempt_login.json()

        if int(response['success']) == 1:
            return True
        else:
            if response['message'] == 'Invalid username/password!':
                raise InvalidLogin('Wrong username or password')
            else:
                raise AccountProblem('Unknown problem while login into Pornhub message:{m}'.format(m=response['message']))
        
        raise AccountProblem('Unknown problem while login into Pornhub')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_pornhub = session.get('http://www.pornhub.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_pornhub.content,self.parser)
        is_sign_out_link = doc.xpath('//li[@class="signOut"]')
        if is_sign_out_link:
            return True
        else:
            return False

if __name__ == '__main__':
    account =  PornHubAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()