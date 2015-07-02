# -*- coding: utf-8 -*-
#!/usr/bin/python
from lxml import etree
from lxml.etree import HTMLParser

from bringyourownproxies.errors import AccountProblem,InvalidLogin,AccountNotActivated
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.sites.account import _Account

__all__ = ['YouPornAccount']

class YouPornAccount(_Account):

    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,username,password,email,**kwargs):
        super(YouPornAccount,self).__init__(username=username,password=password,email=email,**kwargs)

    @classmethod
    def create(cls,username,password,email,gender,**kwargs):

        if gender.lower() == 'm':
            gender = 'male'
        if gender.lower() == 'f':
            gender = 'female'

        http_settings = kwargs.get('http_settings',HttpSettings())

        session = kwargs.get('session',http_settings.session)
        proxy = kwargs.get('proxy',http_settings.proxy)

        session.get('http://www.youporn.com',proxies=proxy)
        ip = session.get('http://www.getip.com/',proxies=proxy)
        register_page = session.get('http://www.youporn.com/register/',proxies=proxy)

        post = {'registration[username]':username,
                'registration[password]':password,
                'registration[confirm_password]':password,
                'registration[email]':email,
                'registration[gender]':gender,
                'registration[terms_of_service]':'1',
                'registration[local_data]':'{}'}

        create_account = session.post('http://www.youporn.com/register/',data=post,proxies=proxy)

        doc = etree.fromstring(create_account.content,HTMLParser())
        errors = []
        find_errors = doc.xpath('//ul[@class="error"]/li')
        if find_errors:
            errors = [e.text for e in find_errors]

        if errors:
            raise AccountProblem('Youporn account creation failed due to errors:{e}'.format(e=' AND '.join(errors)))

        return cls(username=username,password=password,email=email,gender=gender,**kwargs)

    @staticmethod
    def verify_account(http_settings,imap_server,username,password,ssl=True):

        from lxml import etree
        from lxml.etree import HTMLParser,tostring

        clicked_link = _Account.verify_account_in_html_email(http_settings,
                                                        imap_server,
                                                        username,
                                                        password,
                                                        sender='youporn.com',
                                                        clues=('text','Activate Your Free Account'),
                                                        match_substring=True,
                                                        ssl=True)

        doc = etree.fromstring(clicked_link,HTMLParser())
        found_success_msg = doc.xpath('//div[@class="userMessageContent"]//p')
        if found_success_msg:
            p = found_success_msg[0].text
            if p == 'Your account has been activated successfully':
                return True
        else:
            error_msg = doc.xpath('//div[@class="content-inner"]//p')
            if error_msg:
                raise AccountProblem('Failed verifying youporn account due to:{e}'.format(e=error_msg[0].text))

            raise AccountProblem('Failed verifying youporn account due to unknown error')

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
    #account = YouPornAccount('emoneybizzy','money1003','emoneybizzy@gmail.com')
    http_settings = HttpSettings()
    http_settings.set_proxy(ip='127.0.0.1',port=3003)
    #create_account = YouPornAccount.create('timisthebest','wegohardallday','timisthebestdude@gmail.com','m',http_settings=http_settings)
    verify_account = YouPornAccount.verify_account(http_settings,'imap.gmail.com','timisthebestdude@gmail.com','wegohardallday')
    #verify_account = YouPornAccount.verify_account(account.http_settings,'imap.gmail.com','emoneybizzy@gmail.com','money1003')
    #account.login()


