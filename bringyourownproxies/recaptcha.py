# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
import re
import io
import requests

from bringyourownproxies.errors import RecaptchaProblem

def get_new_challenge(key):

    url = 'http://www.google.com/recaptcha/api/challenge?k={k}'.format(k=key)
    challenge_page = requests.get(url)
    challenge_regex = r"challenge\s+:\s+'(.*?)',"
    found_challenge = re.search(challenge_regex,challenge_page.content)

    if found_challenge:
        return found_challenge.group(1)

    raise RecaptchaProblem('Could not find challenge')

def get_image(challenge):
    url = 'http://www.google.com/recaptcha/api/image?c={c}'.format(c=challenge)
    image_page = requests.get(url)
    return io.BytesIO(image_page.content)

