#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin,AccountNotActivated,NotLogined
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

from bringyourownproxies.sites.youporn.profile import YouPornProfile

__all__ = ['YouPornAccount']

class YouPornAccount(_Account):
    
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,username,email,password,**kwargs):
        super(YouPornAccount,self).__init__(username=username,password=password,email=email,**kwargs)

    def login(self):

        login  = self._login(username='login[username]',
                                    password='login[password]',
                                    extra_post_vars={"login[previous]":"",
                                                    "login[local_data]":"{}"},
                                    ajax=True,
                                    post_url='http://www.youporn.com/login/')

        r = login.json()
        
        if not r['success'] :
            if r['response'] == 'Your user is not yet active.  Please try again later.':
                raise AccountNotActivated('YouPorn account needs to be activated by verifying the email provided at signup')
            elif r['response'] ==  'The username or password you entered is incorrect.':
                raise InvalidLogin('Wrong username or password')
            else:
                raise AccountProblem('Response:{response}'.format(response=r['response']))
        return True

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        check_if_logined = session.get('http://www.youporn.com/login/accessuserpages/',proxies=proxy)
        if check_if_logined.url == 'http://www.youporn.com/login/?previous=%2Flogin%2Faccessuserpages%2F':
            return False
        else:
            return True
    def __repr__(self):
        return "<YouPorn's Account(User:{user},Password:{password},Email:{email}>".format(user=self.username,
                                                                                        password=self.password,
                                                                                        email=self.email)


if __name__ == '__main__':
    acct = YouPornAccount(username='tedwantsmore',email='tedwantsmore@gmx.com',password='money1003')
    acct.login()
    print acct.is_logined()