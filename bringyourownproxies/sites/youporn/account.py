#!/usr/bin/python
# -*- coding: utf-8 -*-

from bringyourownproxies.errors import AccountProblem,InvalidLogin,AccountNotActivated,NotLogined
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account

from bringyourownproxies.sites.youporn.profile import YouPornProfile

__all__ = ['YouPornAccount']

class YouPornAccount(_Account):

    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,username,password,email,**kwargs):
        super(YouPornAccount,self).__init__(username=username,password=password,email=email,**kwargs)


    @classmethod
    def create(cls,username,password,email,gender,**kwargs):

        from lxml import etree
        from lxml.etree import HTMLParser

        if gender.lower() == 'm':
            gender = 'male'
        if gender.lower() == 'f':
            gender = 'female'

        http_settings = kwargs.get('http_settings',HttpSettings())

        session = kwargs.get('session',http_settings.session)
        proxy = kwargs.get('proxy',http_settings.proxy)

        session.get('http://www.youporn.com',proxies=proxy)
        ip = session.get('http://www.getip.com/',proxies=proxy)
        with open('/root/Dropbox/get_ip.html','w+') as f:
            f.write(ip.content)
        register_page = session.get('http://www.youporn.com/register/',proxies=proxy)

        with open('/root/Dropbox/youporn_registration_page.html','w+') as f:
            f.write(register_page.content)
        post = {'registration[username]':username,
                'registration[password]':password,
                'registration[confirm_password]':password,
                'registration[email]':email,
                'registration[gender]':gender,
                'registration[terms_of_service]':'1',
                'registration[local_data]':'{}'}

        print post
        create_account = session.post('http://www.youporn.com/register/',data=post,proxies=proxy)

        with open('/root/Dropbox/youporn_outlook_create.html','w+') as f:
            f.write(create_account.content)
        doc = etree.fromstring(create_account.content,HTMLParser())

        inner_content_h1  = doc.xpath('//div[@class="content-inner"]/h1')
        found_success_msg = False
        if inner_content_h1:
            for h1 in inner_content_h1:
                if h1.text:
                    if 'Please check your email and confirm your address.' in h1.text:
                        found_success_msg = True
                        break

        if not found_success_msg:
            raise AccountProblem('Did get message back saying to confirm email address. '\
                                 'Youporn account creation failed')

        return cls(username=username,password=password,email=email,gender=gender,**kwargs)

    @staticmethod
    def verify_account(http_settings,imap_server,username,password,ssl=True):

        from lxml import etree
        from lxml.etree import HTMLParser,tostring

        clicked_link = _Account.verify_account(http_settings,
                                                imap_server,
                                                username,
                                                password,
                                                sender='youporn.com',
                                                clues=('text','Activate Your Free Account'),
                                                match_substring=True,
                                                ssl=True)

        doc = etree.fromstring(clicked_link,HTMLParser())
        inner_content = doc.xpath('//div[@class="content-inner"]')
        if inner_content:
           inner_doc = etree.fromstring(tostring(inner_content[0]),HTMLParser())
           h1 = inner_doc.xpath('//h1')
           if h1:
               if h1[0].text:
                   if 'An error has occured!' in h1[0].text:
                       error_txt = inner_doc.xpath('//p')[0].text
                       raise AccountProblem('Failed verifying youporn account due to:{e}'.format(e=error_txt))

        raise AccountProblem('Failed verifying youporn account due to unknown error')

        with open('/root/Dropbox/youporn_outlook_clicked.html','w+') as f:
            f.write(clicked_link)

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
    http_settings.set_proxy(ip='127.0.0.1',port=3001)
    create_account = YouPornAccount.create('IamprettyFamous1003','money1003','iamprettyfamouskid@gmail.com','m',http_settings=http_settings)
    verify_account = YouPornAccount.verify_account(http_settings,'imap.gmail.com','Iamprettyfamouskid@gmail.com','money1003')
    #verify_account = YouPornAccount.verify_account(account.http_settings,'imap.gmail.com','emoneybizzy@gmail.com','money1003')
    #account.login()


