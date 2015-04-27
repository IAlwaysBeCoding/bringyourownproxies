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


    @staticmethod
    def verify_account(http_settings,imap_server,username,password,ssl=True):

        import re
        from lxml import etree
        from lxml.etree import HTMLParser
        from imbox import Imbox

        from bringyourownproxies.errors import VerificationLinkNotFound

        email_box = Imbox(imap_server,username,password,ssl)

        msgs = email_box.messages(sent_from='youporn.com')

        verification_link_regex = r'following\s+this\s+link:\s+(.*?)\s+Or'
        verification_link = None

        for msg in msgs:
           uid,email = msg
           doc = etree.fromstring(email.body['html'][0],HTMLParser())
           for a in doc.xpath('//a'):
               if a.text:
                   if 'Activate Your Free Account' in a.text:
                       verification_link = a.attrib['href']
                       print verification_link

        if not verification_link:
            raise AccountProblem('Cannot find email verification link sent from youporn.com')

        session = http_settings.session
        proxy = http_settings.proxy

        verify = session.get(verification_link,proxies=proxy)

        with open('/root/Dropbox/verify_youporn.html', 'w+') as f:
            f.write(verify.content)

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

if __name__ == '__main__':
    from bringyourownproxies.sites import YouPornAccount
    account = YouPornAccount('emoneybizzy','emoneybizzy@gmail.com','money1003')
    #account.login()
    verify_account = YouPornAccount.verify_account(account.http_settings,'imap.gmail.com','emoneybizzy@gmail.com','money1003')
    account.login()

