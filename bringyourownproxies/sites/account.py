#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import etree
from lxml.etree import HTMLParser, tostring

from bringyourownproxies.captcha import (
    DEFAULT_CAPTCHA_SOLVER,
    DEFAULT_CAPTCHA_MAXIMUM_WAITING,
    DeathByCaptcha,
    DeathByCaptchaProblem,
    CaptchaProblem)
from bringyourownproxies.errors import InvalidLogin, AccountProblem
from bringyourownproxies.account import OnlineAccount

from bringyourownproxies.sites.errors import CouldNotFindVar

ERROR_MESSAGES_XPATH = ['//div[@class="message_error"]/text()']
WRONG_PASSWORD_MESSAGES = [
    'Invalid Username or Password. Username and Password are case-sensitive.',
    '! Invalid Username or Password. Username and Password are case-sensitive.']

SIGN_OUT_XPATH = ['//li[@class="logout"]', '//a[@href="/sign-out/"]']
JSON_SUCCESS_KEY = []
JSON_ERROR_KEY = []
JSON_ERROR_MESSAGES_KEY = []


class _Account(OnlineAccount):

    def _login(self, **kwargs):

        username = kwargs.get('username', 'username')
        password = kwargs.get('password', 'password')
        email = kwargs.get('email', self.email)
        ajax = kwargs.get('ajax', False)
        extra_headers = kwargs.get('extra_headers', {})
        before_post_url = kwargs.get('before_post_url', None)
        before_post_url_vars = kwargs.get('before_post_url_vars', {})
        post_url = kwargs.get('post_url', None)
        post_url_vars = kwargs.get('post_url_vars', {})
        extra_post_vars = kwargs.get('extra_post_vars', {})
        post_vars = kwargs.get(
            'post_vars', {
                username: self.username, password: self.password})

        session = self.http_settings.session
        proxy = self.http_settings.proxy

        if not self.SITE_URL.startswith('http://') or \
                not self.SITE_URL.startswith('https://'):
            domain_url = 'http://{url}'.format(url=self.SITE_URL)

        go_to_site = session.get(domain_url, proxies=proxy)

        if before_post_url:

            before_posting_url = session.get(before_post_url, proxies=proxy)

            doc = self.etree.fromstring(before_posting_url.content, self.parser)
            for var in before_post_url_vars:
                if before_post_url_vars[var] is None:
                    get_var = doc.xpath(
                        '//input[@name="{name}"]'.format(name=var))
                    if get_var:
                        post_vars[var] = get_var[0].attrib['value']
                    else:
                        raise CouldNotFindVar(
                            'Could not find {v} in url:{u}'.format(
                                v=var))
                else:
                    post_vars[var] = before_post_url_vars[var]

        if ajax:
            session.headers.update({"X-Requested-With": "XMLHttpRequest"})

        for extra in extra_post_vars:
            post_vars[extra] = extra_post_vars[extra]

        for header in extra_headers:
            session.headers[header] = extra_headers[header]

        attempt_login = session.post(post_url, data=post_vars, proxies=proxy)

        return attempt_login

    @staticmethod
    def verify_account(
            http_settings,
            imap_server,
            username,
            password,
            sender,
            clues,
            match_substring=False,
            ssl=True):

        import re
        from lxml import etree
        from lxml.etree import HTMLParser
        from imbox import Imbox

        from bringyourownproxies.errors import VerificationLinkNotFound, AccountProblem

        email_box = Imbox(imap_server, username, password, ssl)
        msgs = email_box.messages(sent_from=sender)
        verification_link = None

        if isinstance(clues, (list, tuple)):
            if not isinstance(clues[0], (list, tuple)):
                if len(clues) != 2:
                    raise AccountProblem(
                        'clues needs to be a list/tuple each containing 2 tuple/list items')
                else:
                    clues = [clues]
            else:
                for clue in clues:
                    if isinstance(clue, (list, tuple)):
                        if len(clue) != 2:
                            raise AccountProblem(
                                'clues needs to be a list/tuple each containing 2 tuple/list items')
                    else:
                        raise AccountProblem(
                            'clues needs to be a list/tuple each containing 2 tuple/list items')
        else:
            raise AccountProblem(
                'clues needs to be a list/tuple each containing 2 tuple/list items')

        for msg in msgs:
            uid, email = msg
            doc = etree.fromstring(email.body['html'][0], HTMLParser())
            for a in doc.xpath('//a'):

                found_verification_link = False
                for clue in clues:
                    clue_attrib, clue_value = clue

                    if clue_attrib == 'text':
                        value_found = a.text
                    else:
                        value_found = a.attrib[clue_attrib]
                    if match_substring:
                        if value_found:
                            if clue_value in value_found:
                                verification_link = a.attrib['href']
                                found_verification_link = True
                                break

                    if clue_value == value_found:
                        verification_link = a.attrib['href']
                        found_verification_link = True
                        break

        if not verification_link:
            raise VerificationLinkNotFound(
                'Cannot find email verification link sent from:{sender}'.format(
                    sender=sender))

        session = http_settings.session
        proxy = http_settings.proxy

        verify = session.get(verification_link, proxies=proxy)

        return verify.content

    @staticmethod
    def submit_captcha_and_wait(
            captcha,
            maximum_waiting_time=DEFAULT_CAPTCHA_MAXIMUM_WAITING,
            captcha_solver=DEFAULT_CAPTCHA_SOLVER):

        import time

        def poll_death_by_captcha(captcha_id):
            import json
            import requests
            url = 'http://api.dbcapi.me/api/captcha/' \
                '{captcha_id}'.format(captcha_id=captcha_id)

            check_status = requests.get(
                url, headers={
                    'Accept': 'application/json'})

            try:
                response = json.loads(check_status.content)
                return response['text']

            except ValueError:
                if check_status.content == 'not+found':
                    raise DeathByCaptchaProblem('Not a valid captcha id')

        captcha_response = None

        if isinstance(captcha_solver, DeathByCaptcha):

            response = captcha_solver.upload(captcha)
            if 'error' in response:
                raise DeathByCaptchaProblem(
                    'Error while submitting '
                    'captcha:{error}'.format(
                        error=response['error']))

            if 'is_correct' in response:
                if response['is_correct']:
                    if not response['text']:
                        current_waiting_time = 0

                        while current_waiting_time < maximum_waiting_time:
                            poll = poll_death_by_captcha(response['captcha'])
                            if poll:
                                captcha_response = poll
                                break
                            else:
                                time.sleep(5)
                                current_waiting_time += 5

                        if not captcha_response:
                            raise DeathByCaptchaProblem(
                                'Timed out, took more than '
                                'than the maximum amount of '
                                'time:{t} allowed to retrieve a '
                                'response'.format(
                                    t=maximum_waiting_time))
                    else:
                        captcha_response = response['text']
                else:
                    raise DeathByCaptchaProblem('Captcha is incorrect')
            else:
                raise DeathByCaptchaProblem(
                    'Unknown response by deathbycaptcha')

            return captcha_response
        else:
            raise CaptchaProblem('Unknown captcha solver')

    def _find_sign_out(self, response, **kwargs):

        sign_out_xpath = kwargs.get('sign_out_xpath', None)

        html = response.content
        doc = self.etree.fromstring(html, self.parser)

        found = False
        if sign_out_xpath:
            if doc.xpath(sign_out_xpath):
                found = True
        else:
            for xpath in SIGN_OUT_XPATH:
                if doc.xpath(xpath):
                    found = True
                    break

        return found

    def _is_logined(self, **kwargs):

        session = self.http_settings.session
        proxy = self.http_settings.proxy

        if not self.SITE_URL.startswith('http://') or \
                not self.SITE_URL.startswith('https://'):
            domain_url = 'http://{url}'.format(url=self.SITE_URL)
        go_to_site = session.get(domain_url, proxies=proxy)

        is_signed_in = self._find_sign_out(go_to_site, **kwargs)

        return is_signed_in

    def _find_login_errors(self, response, **kwargs):
        error_msg_xpath = kwargs.get('error_msg_xpath', ERROR_MESSAGES_XPATH)
        wrong_pass_msg = kwargs.get('wrong_pass_msg', WRONG_PASSWORD_MESSAGES)
        use_username = kwargs.get('use_username', True)
        use_password = kwargs.get('use_password', True)

        doc = self.etree.fromstring(response.content, self.parser)

        if not isinstance(error_msg_xpath, (list, tuple)):
            error_msg_xpath = [error_msg_xpath]

        if not isinstance(wrong_pass_msg, (list, tuple)):
            wrong_pass_msg = [wrong_pass_msg]

        for xpath in error_msg_xpath:
            xpath_error = doc.xpath(xpath)

            if xpath_error:
                error_msg = xpath_error[0]
                has_wrong_pass = self._is_wrong_password(
                    error=error_msg,
                    look_in_these=wrong_pass_msg)

                if has_wrong_pass:
                    raise InvalidLogin('Wrong username(email) or password')

                raise AccountProblem(
                    'Error:{error} '
                    ' while login into {site}'
                    ' username:{username} '
                    ' password:{password} '
                    ' email:{email}'.format(
                        error=error_msg,
                        site=self.SITE,
                        username=self.username,
                        password=self.password,
                        email=self.email))

    def _is_wrong_password(self, error, **kwargs):
        look_in_these = kwargs.get('look_in_these', WRONG_PASSWORD_MESSAGES)
        if not isinstance(look_in_these, (list, tuple)):
            messages_to_match = [look_in_these]

        else:
            if isinstance(look_in_these, (list, tuple)):
                messages_to_match = look_in_these
            else:
                raise TypeError(
                    'look_in_these needs to be a list,tuple or a str containing the wrong msg password to look for')

        for match in messages_to_match:
            if match.strip() == error.strip():
                return True
                break

        return False


if __name__ == '__main__':
    captcha_solver = DeathByCaptcha('tedwantsmore', 'money1003')
    response = _Account.submit_captcha_and_wait(
        '/root/Dropbox/recaptcha.png',
        captcha_solver,
        180)
    print response
