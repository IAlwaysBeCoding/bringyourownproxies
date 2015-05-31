# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
import requests
import path

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from bringyourownproxies.recaptcha import get_new_challenge as get_new_recaptcha_challenge
from bringyourownproxies.recaptcha import get_image as get_recaptcha_image
from bringyourownproxies.deathbycaptcha import SocketClient as DeathByCaptcha
from bringyourownproxies.errors import CaptchaProblem,DeathByCaptchaProblem,RecaptchaProblem

CAPTCHA_SOLVERS = [DeathByCaptcha]
DEFAULT_CAPTCHA_MAXIMUM_WAITING = 180
DEFAULT_CAPTCHA_USER = 'tedwantsmore'
DEFAULT_CAPTCHA_PASSWORD = 'money1003'
DEFAULT_CAPTCHA_SOLVER = DeathByCaptcha(DEFAULT_CAPTCHA_USER,DEFAULT_CAPTCHA_PASSWORD)

def submit_captcha_and_wait(
        captcha,
        maximum_waiting_time=DEFAULT_CAPTCHA_MAXIMUM_WAITING,
        captcha_solver=DEFAULT_CAPTCHA_SOLVER,
        return_captcha_id=False):

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

        if return_captcha_id:
            return (response['captcha'],captcha_response)
        else:
            return captcha_response
    else:
        raise CaptchaProblem('Unknown captcha solver')

def report_bad_captcha(captcha_solver,captcha_id):
    if isinstance(captcha_solver, DeathByCaptcha):
        captcha_solver.report(captcha_id)

