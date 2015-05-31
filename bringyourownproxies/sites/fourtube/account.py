# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

__all__ = ['_4tubeAccount']

class _4tubeAccount(_Account):
    
    SITE = '_4tube'
    SITE_URL = 'www.4tube.com'
    
    def __init__(self,username,password,email,**kwargs):
        super(_4tubeAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        attempt_login  = self._login(username='_username',
                                    password='_password',
                                    extra_post_vars={"_target_path":"/"},
                                    ajax=True,
                                    before_post_url='http://www.4tube.com/login',
                                    post_url='http://www.4tube.com/login_check')

        response =  attempt_login.json()
        
        if response['result'] == 'ok':
            return True

        raise AccountProblem('Something went wrong while login into 4tube.com')
        
    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        go_to_porntube = session.get('http://www.4tube.com/users/{username}/edit'.format(username=self.username),proxies=proxy)

        doc = self.etree.fromstring(go_to_porntube.content,self.parser)
        get_title = doc.xpath('//title')
        if get_title:

            if 'Page not found' in get_title[0].text:
                return False
            else:
                return True

