# -*- coding: utf-8 utf-*-
#!/usr/bin/python
import random

from requests.cookies import create_cookie

from bringyourownproxies.utils import generate_timestamp
from bringyourownproxies.errors import AccountProblem
from bringyourownproxies.sites.account import _Account

__all__ = ['XhamsterAccount']

def generate_stats():

	math_random = float('.{n}'.format(n=random.randrange(1000000000000000,9999999999999999,1)))
	res1 =  hex(int(math_random * 10000000))[2:]
	timestamp = generate_timestamp()
	res2 = hex(timestamp)[2:][0:8]
	return (res1,res2)


class XhamsterAccount(_Account):

    SITE = 'xHamster'
    SITE_URL = 'www.xhamster.com'

    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(XhamsterAccount,self).__init__(username=username,password=password,email=email,**kwargs)

    def login(self):

        session = self.http_settings.session
        proxy = self.http_settings.proxy

        go_to_xhamster = session.get('http://www.xhamster.com',proxies=proxy)

        timestamp = generate_timestamp()
        get_stats = generate_stats()
        stats = "{res1}:{res2}".format(res1=get_stats[0],res2=get_stats[1])
        xsid = create_cookie('xsid',stats)
        session.cookies._cookies['.xhamster.com']['/']['xsid'] = xsid

        url="http://xhamster.com/ajax/login.php?act=login&ref=" \
            "http%3A%2F%2Fxhamster.com%2F&stats={stats}&username={username}" \
            "&password={password}&remember={remember}&_={timestamp}".format(stats=stats,
                                                                            username=self.username,
                                                                            password=self.password,
                                                                            remember="on" if self.remember_me else "off",
                                                                            timestamp=timestamp)

        session.headers.update({"X-Requested-With":"XMLHttpRequest",
                                "Accept":"Accept:text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
                                "Referer":"http://xhamster.com/login.php"})
        attempt_login = session.get(url,proxies=proxy)
        if 'login.stats' in attempt_login.content:
            return True
        else:
            raise AccountProblem('Unknown problem while login into xhamster')

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        go_to_xhamster = session.get('http://www.Xhamster.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_xhamster.content,self.parser)
        find_sign_out_link = doc.xpath('//a[@class="l1"]')
        found_sign_out_link = False
        for a in find_sign_out_link:
            if a.text == 'Logout':
                found_sign_out_link = True
                break

        if found_sign_out_link:
            return True
        else:
            return False


