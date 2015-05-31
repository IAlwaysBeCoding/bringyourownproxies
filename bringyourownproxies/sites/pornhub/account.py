# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin,ParsingProblem
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account

__all__ = ['PornhubAccount']

class PornhubAccount(_Account):

    SITE = 'Pornhub'
    SITE_URL = 'www.pornhub.com'

    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False

        super(PornhubAccount,self).__init__(username=username,password=password,email=email,**kwargs)

    @classmethod
    def create(cls,username,password,email,**kwargs):

        from lxml import etree
        from lxml.etree import HTMLParser

        from bringyourownproxies.httpclient import HttpSettings
        from bringyourownproxies.errors import CannotFindVar

        remember_me = kwargs.get('remember_me',False)
        http_settings = kwargs.get('http_settings',HttpSettings())
        session = http_settings.session
        proxy = http_settings.proxy

        session.get('http://www.pornhub.com',proxies=proxy)

        create_page = session.get('http://www.pornhub.com/create_account',proxies=proxy)

        doc = etree.fromstring(create_page.content,HTMLParser())

        found_signup_key = doc.xpath('//input[@name="signup_key"]/@value')
        found_signup_hash = doc.xpath('//input[@name="signup_hash"]/@value')
        found_signup_id = doc.xpath('//input[@name="signup_id"]/@value')

        if not found_signup_key:
            raise CannotFindVar('Cannot find signup_key in pornhub.com')
        if not found_signup_hash:
            raise CannotFindVar('Cannot find signup_hash in pornhub.com')
        if not found_signup_id:
            raise CannotFindVar('Cannot find signup_id in pornhub.com')

        signup_key = found_signup_key[0]
        signup_hash = found_signup_hash[0]
        signup_id = found_signup_id[0]

        post = {'signup_key':signup_key,
                'signup_hash':signup_hash,
                'signup_id':signup_id,
                'check_what':'username',
                'email':email,
                'username':username,
                'password':password,
                'agreed':'1'}
        session.headers.update({'X-Requested-With':'XMLHttpRequest'})
        session.post('http://www.pornhub.com/user/create_account_check',proxies=proxy)

        create_account = session.post('http://www.pornhub.com/create_account',data=post,proxies=proxy)

        errors = []
        doc = etree.fromstring(create_account.content,HTMLParser())
        found_errors = doc.xpath('//div[@class="error"]/div')

        if found_errors:
            errors = [error.text[2:len(error.text)-1] for error in found_errors]
            raise AccountProblem('Failed creating account at pornhub due to errors:{e}'.format(e=' AND '.join(errors)))
        found_confirmation = doc.xpath('//div[@class="sprite-signup-confirmation absolute"]')

        if found_confirmation:
            return True
        else:
            raise AccountProblem('Failed creating account at pornhub for unknown problem')

    @staticmethod
    def verify_account(http_settings,imap_server,username,password,ssl=True):

        from lxml import etree
        from lxml.etree import HTMLParser,tostring

        clicked_link = _Account.verify_account_in_html_email(http_settings,
                                                        imap_server,
                                                        username,
                                                        password,
                                                        sender='pornhub.com',
                                                        clues=('text','Activate Your Account'),
                                                        match_substring=True,
                                                        ssl=True)

        doc = etree.fromstring(clicked_link,HTMLParser())
        found_success_msg = doc.xpath('//div[@class="success"]')
        if found_success_msg:
            return True
        else:
            error_msg = doc.xpath('//div[@class="error"]//div')
            if error_msg:
                raise AccountProblem('Failed verifying pornhub account ' \
                                     'due to:{e}'.format(
                                         e=error_msg[0].text[2:len(error_msg[0].text)-1]))

            raise AccountProblem('Failed verifying pornhub account due to unknown error')


    def login(self):

        attempt_login  = self._login(extra_post_vars = {"loginPage":1,
                                                        "redirectTo":"",
                                                        "remember_me": "on" if self.remember_me else "off",
                                                        "submit_login":"true"},
                                    ajax=True,
                                    before_post_url='http://www.pornhub.com/login',
                                    before_post_url_vars={"login_key":None,"login_hash":None},
                                    post_url='http://www.pornhub.com/front/login_json')

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
        return self._is_logined(sign_out_xpath='//li[@class="signOut"]')

if __name__ == '__main__':
    from bringyourownproxies.httpclient import HttpSettings
    username = 'timisthebest'
    password = 'wegohardallday'
    email = 'timisthebestdude@gmail.com'
    http_settings = HttpSettings()
    http_settings.set_proxy('localhost',3003)
    #create_account = PornhubAccount.create(username,password,email)
    account = PornhubAccount(username,password,email,http_settins=http_settings)
    #account.login()
    verify_account = PornhubAccount.verify_account(account.http_settings,'imap.gmail.com',email,password)
    #account = PornhubAccount(username,password,email)
