# -*- coding: utf-8 -*-
#!/usr/bin/python
import re
import json

from bringyourownproxies.errors import AccountProblem, InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account

from lxml import etree
from lxml.etree import HTMLParser

from bringyourownproxies.errors import CannotFindVar
from bringyourownproxies.captcha import (
                            DEFAULT_CAPTCHA_SOLVER,
                            DEFAULT_CAPTCHA_MAXIMUM_WAITING,
                            get_new_recaptcha_challenge,
                            get_recaptcha_image)


__all__ = ['RedTubeAccount']


class RedTubeAccount(_Account):

    SITE = 'RedTube'
    SITE_URL = 'www.redtube.com'

    def __init__(self, username, password, email, **kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get(
            'remember_me',
            False) else False

        super(
            RedTubeAccount,
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

    def login(self):
        attempt_login = self._login(
            username='sUsername',
            password='sPassword',
            extra_post_vars={
                "iFriendID": 0,
                "iObjectID": 0,
                "iObjectType": 0,
                "bRemember": "2" if self.remember_me else "1",
                "do": "Log in"},
            ajax=True,
            post_url='http://www.redtube.com/htmllogin')

        is_success = re.findall(
            r'parent.loginSuccess\((.*?)\);',
            attempt_login.content,
            re.I | re.M)

        if is_success:
            try:
                response = json.loads(is_success[0])
            except:
                raise AccountProblem('Could not read json login response')
            if response['success']:
                return True

        else:
            doc = self.etree.fromstring(attempt_login.content, self.parser)
            find_errors = doc.xpath('//p[@class="error-summary"]/text()')
            if find_errors:
                if find_errors[0] == 'Username or password incorrect. Please try again.':
                    raise InvalidLogin('Wrong username or password')

        raise AccountProblem(
            'Unknown error while trying to loging into redtube.com')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        go_to_redtube = session.get(
            'http://www.redtube.com/community',
            proxies=proxy)

        doc = self.etree.fromstring(go_to_redtube.content, self.parser)
        find_all_a = doc.xpath('//a[@href="javascript:;" and @onclick]')
        found_login_a = False
        for a in find_all_a:

            if 'showLogin()' in a.attrib['onclick']:
                found_login_a = True
                break
        if found_login_a:
            return False
        else:
            return True
