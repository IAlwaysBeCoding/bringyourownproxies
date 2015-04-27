#!/usr/bin/python
import requests
import path

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from bringyourownproxies.deathbycaptcha import SocketClient as DeathByCaptcha
from bringyourownproxies.errors import CaptchaProblem,DeathByCaptchaProblem

CAPTCHA_SOLVERS = [DeathByCaptcha]
DEFAULT_CAPTCHA_MAXIMUM_WAITING = 180
DEFAULT_CAPTCHA_USER = 'tedwantsmore'
DEFAULT_CAPTCHA_PASSWORD = 'money1003'
DEFAULT_CAPTCHA_SOLVER = DeathByCaptcha(DEFAULT_CAPTCHA_USER,DEFAULT_CAPTCHA_PASSWORD)


if __name__ == '__main__':
    captcha_solver = DeathByCaptcha('tedwantsmore','money1003')
    captcha_solver.submit_captcha('/root/Dropbox/recaptcha.png')
