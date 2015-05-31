# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin,CannotFindVar
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.sites.account import _Account

__all__ = ['DrTuberAccount']

class DrTuberAccount(_Account):

    SITE = 'DrTuber'
    SITE_URL = 'www.drTuber.com'

    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(DrTuberAccount,self).__init__(username=username,password=password,email=email,**kwargs)

    @classmethod
    def create(cls,username,password,email,gender,**kwargs):

        import io
        from lxml import etree
        from lxml.etree import HTMLParser

        def get_captcha_image():
            download_captcha = session.get('http://www.drtuber.com/captcha',proxies=proxy)
            captcha_data = io.BytesIO(download_captcha.content)
            return captcha_data

        if gender.lower() == 'm':
            gender = 'Male'
        if gender.lower() == 'f':
            gender = 'Female'

        http_settings = kwargs.get('http_settings',HttpSettings())

        session = kwargs.get('session',http_settings.session)
        proxy = kwargs.get('proxy',http_settings.proxy)
        captcha_solver = kwargs.get('captcha_solver',DEFAULT_CAPTCHA_SOLVER)
        maximum_waiting_time = kwargs.get('maximum_waiting_time',DEFAULT_CAPTCHA_MAXIMUM_WAITING)


        url = 'http://www.drtuber.com/ajax/popup_forms?form=signup'
        sign_up_form = session.get(url,proxies=proxy)

        doc = etree.fromstring(sign_up_form.json()['answer'],HTMLParser())

        found_form_id = doc.xpath('//input[@name="formId"]/@value')
        if not found_form_id:
            raise CannotFindVar('Cannot find formId , required for creating an account')

        form_id = found_form_id[0]

        captcha_image = get_captcha_image()
        captcha_response = cls.submit_captcha_and_wait(captcha_image,
                                                       maximum_waiting_time=maximum_waiting_time,
                                                       captcha_solver=captcha_solver)

        url = 'http://www.drtuber.com/signup/do?ajax=true&json=true'

        post = {'username':username,
                'password':password,
                'password_confirm':password,
                'gender':gender,
                'email':email,
                'verification':captcha_response,
                'terms':'on',
                'age':'on',
                'formId':form_id,
                'type':'free',
                'redirectUrl':'/',
                'from':''}

        create_account = session.post(url,data=post,proxies=proxy)
        response = create_account.json()

        if response['errors']:
            raise AccountProblem('Cannot create drtuber account due to errors:' \
                                 '{e}'.format(e=" AND ".join(response['errors'])))

        remember_me = kwargs.get('remember_me',False)

        return cls(username=username,password=password,email=email,remember_me=remember_me,gender=gender)

    def login(self):

        attempt_login  = self._login(extra_post_vars={
                                                    'submit_login':'true',
                                                    'login_remember':'true' if self.remember_me else 'false'
                                                    },
                                    ajax=True,
                                    before_post_url='http://www.drtuber.com/ajax/popup_forms?form=login',
                                    post_url='http://www.drtuber.com/ajax/login')

        result = attempt_login.json()

        if result['success']:
            return True
        else:
            if result['error'] == 'Invalid username and/or password!':
                raise InvalidLogin('Wrong username or password')
        raise AccountProblem('Unknown problem while login into DrTuber message:{e}'.format(e=result['error']))

    def is_logined(self):
        return self._is_logined(sign_out_xpath='//a[@href="/logout"]')

if __name__ == '__main__':
    from bringyourownproxies.sites import DrTuberAccount
    #account = DrTuberAccount.create('emoneybizzy','money1003','emoneybizzy@gmail.com','m')
    #verify = DrTuberAccount.verify_account('imap.gmail.com','emoneybizzy@gmail.com','money1003')



