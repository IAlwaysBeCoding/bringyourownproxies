# -*- coding: utf-8 -*-
#!/usr/bin/python
from lxml import etree
from lxml.etree import HTMLParser

from bringyourownproxies.errors import AccountProblem,CannotFindVar
from bringyourownproxies.captcha import (
                            DEFAULT_CAPTCHA_SOLVER,
                            DEFAULT_CAPTCHA_MAXIMUM_WAITING,
                            CaptchaProblem,
                            get_new_recaptcha_challenge,
                            get_recaptcha_image)

from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account

__all__ = ['XvideosAccount']

class XvideosAccount(_Account):

    SITE = 'Xvideos'
    SITE_URL = 'www.xvideos.com'

    def __init__(self, username, password, email, **kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get(
            'remember_me',
            False) else False

        super(
            XvideosAccount,
            self).__init__(
            username=username,
            password=password,
            email=email,
            **kwargs)

    @classmethod
    def create(
            cls,
            username,
            password,
            email,
            gender,
            name,
            first_name,
            birthdate,
            country,
            region,
            city,
            **kwargs):

        def get_recaptcha_key(html):
            doc = etree.fromstring(html, HTMLParser())
            found_captcha_key = doc.xpath('//div[@id="signupCaptcha"]/script')

            if not found_captcha_key:
                raise CannotFindVar('Cannot find recaptcha key for xvideos.com')
            return found_captcha_key[0].attrib['src'].replace(
                'http://www.google.com/recaptcha/api/challenge?k=',
                '')

        def get_sign_up_errors(html):
            errors = []
            doc = etree.fromstring(html, HTMLParser())

            for possible_error in doc.xpath('//*[@class="inlineError"]'):
                if possible_error.text:
                    errors.append(possible_error.text)

            return errors

        if gender.lower() == 'm':
            gender = 'Man'
        if gender.lower() == 'f':
            gender = 'Woman'

        if len(birthdate.split('/')) != 3:
            raise AccountProblem('Birthday does not match mm/dd/yyyy format')

        birth_day = birthdate.split('/')[0]
        birth_month = birthdate.split('/')[1]
        birth_year = birthdate.split('/')[2]

        http_settings = kwargs.get('http_settings', HttpSettings())

        session = kwargs.get('session', http_settings.session)
        proxy = kwargs.get('proxy', http_settings.proxy)
        captcha_solver = kwargs.get('captcha_solver', DEFAULT_CAPTCHA_SOLVER)
        maximum_waiting_time = kwargs.get(
            'maximum_waiting_time',
            DEFAULT_CAPTCHA_MAXIMUM_WAITING)
        remember_me = kwargs.get('remember_me', False)

        session.get('http://www.xvideos.com', proxies=proxy)
        create_page = session.get(
            'http://upload.xvideos.com/account/create',
            proxies=proxy)

        recaptcha_key = get_recaptcha_key(html=create_page.content)
        recaptcha_challenge = get_new_recaptcha_challenge(key=recaptcha_key)

        captcha_image = get_recaptcha_image(challenge=recaptcha_challenge)
        captcha_response = cls.submit_captcha_and_wait(
                                                    captcha_image,
                                                    captcha_solver=captcha_solver,
                                                    maximum_waiting_time=maximum_waiting_time)

        post = {'referer': '',
                'recaptcha_challenge_field': recaptcha_challenge,
                'recaptcha_response_field': captcha_response,
                'creer': '1',
                'email': email,
                'profile_name': username,
                'password': password,
                'password_confirm': password,
                'nom': name,
                'prenom': first_name,
                'birth_year': birth_year,
                'birth_month': birth_month,
                'birth_day': birth_day,
                'sexe': gender,
                'pays': country,
                'region': region,
                'ville': city}

        create_account = session.post(
            'http://upload.xvideos.com/account/create',
            data=post,
            proxies=proxy)
        sign_up_errors = get_sign_up_errors(html=create_account.content)

        if sign_up_errors:
            for error in sign_up_errors:
                if error == 'Bad CAPTCHA.':
                    raise CaptchaProblem('Wrong captcha')

            raise AccountProblem(
                'Failed creating xvideos.com '
                'account due to errors:{e}'.format(
                    e=' AND '.join(sign_up_errors)))

        return cls(username=username,
                   password=password,
                   email=email,
                   gender=gender,
                   name=name,
                   first_name=first_name,
                   birthdate=birthdate,
                   country=country,
                   region=region,
                   city=city,
                   remember_me=remember_me)

    @staticmethod
    def verify_account(http_settings,imap_server,username,password,ssl=True):

        clicked_link = _Account.verify_account_in_plain_email(http_settings,
                                                            imap_server,
                                                            username,
                                                            password,
                                                            sender='xvideos.com',
                                                            regexes=(r'this\s+URL:\s+(.*?).\s+',1),
                                                            ssl=True)


        doc = etree.fromstring(clicked_link,HTMLParser())
        found_success_msg = doc.xpath('//p[@class="inlineOK"]')
        if found_success_msg:
            p = found_success_msg[0].text
            if p == 'Your email is now validated.':
                return True
        else:
            raise AccountProblem('Failed verifying youporn account due to unknown error')

    def login(self):
        attempt_login = self._login(
            use_username=False,
            extra_post_vars={
                "referer": "http://www.xvideos.com/",
                "login": self.email,
                "rememberme": "on" if self.remember_me else "off",
                "log": "Login to your account"},
            post_url='http://upload.xvideos.com/account')

        self._find_login_errors(
            response=attempt_login,
            error_msg_xpath='//p[@class="inlineError form_global_error"]/text()',
            wrong_pass_msg='Bad username or password.')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        go_to_sex = session.get(
            'http://upload.xvideos.com/account',
            proxies=proxy)
        doc = self.etree.fromstring(go_to_sex.content, self.parser)

        if doc.xpath('//form[@id="signinForm"]'):
            return False
        else:
            return True

if __name__ == '__main__':
    username = 'timisthebestdude'
    password = 'wegohardallday'
    email = 'timisthebestdude@gmail.com'
    gender = 'm'
    first_name = 'Derek'
    name = 'Derek'
    birthdate = '01/03/1989'
    country = 'US'
    region = 'CA'
    city = 'West Sacramento'
    http_settings = HttpSettings()
    http_settings.set_proxy(ip='127.0.0.1',port=3003)
    '''
    create_account = XvideosAccount.create(username,
                                        password,
                                        email,
                                        gender,
                                        name,
                                        first_name,
                                        birthdate,
                                        country,
                                        region,
                                        city,
                                        http_settings=http_settings)
    '''
    #create_account = YouPornAccount.create('timisthebest','wegohardallday','timisthebestdude@gmail.com','m',http_settings=http_settings)
    account = XvideosAccount(username,password,email,http_settings=http_settings)
    account.login()

    verify_account = XvideosAccount.verify_account(account.http_settings,'imap.gmail.com','timisthebestdude@gmail.com','wegohardallday')

