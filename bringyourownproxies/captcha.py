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


