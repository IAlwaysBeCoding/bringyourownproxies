#!/usr/bin/python
import base64

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

class YouJizzAccount(_Account):
    
    SITE = 'YouJizz'
    SITE_URL = 'www.youjizz.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(YouJizzAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        attempt_login  = self._login(username="ahd_username",
                                    use_password=False,
                                    extra_post_vars={"ahd_password":base64.b64encode(self.password),
                                                    "Submit":"Login",
                                                    "rememberme":"on" if self.remember_me else "off"},
                                    ajax=True,
                                    post_url='http://www.youjizz.com/login_auth.php')

        doc = self.etree.fromstring(attempt_login.content,self.parser)

        if doc.xpath('//a[@href="/logout.php"]'):
            return True
        else:
            find_error_p = doc.xpath('//p')
            if find_error_p:
                for p in find_error_p:
                    if p.text.strip() == 'The login information you have provided was incorrect. Please try again.':
                        raise InvalidLogin('Wrong username or password')
        
        raise AccountProblem('Unknown problem while login into YouJizz')


    def is_logined(self):
        return self._is_logined(sign_out_xpath='//a[@href="/logout.php"]')

if __name__ == '__main__':
    account =  YouJizzAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()