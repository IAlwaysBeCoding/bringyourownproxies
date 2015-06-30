# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

__all__ = ['KeezMoviesAccount']

class KeezMoviesAccount(_Account):
    
    SITE = 'KeezMovies'
    SITE_URL = 'www.keezmovies.com'
    
    def __init__(self,username,password,email,**kwargs):
        super(KeezMoviesAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        attempt_login  = self._login(extra_headers={"Accept":"application/json, text/javascript, */*; q=0.01"},
                                    ajax=True,
                                    post_url='http://www.keezmovies.com/ajax/login')
        
        response = attempt_login.json()

        if response['response']['success']:
            return True
        else:
            raise AccountProblem('Unknown problem while login into KeezMovies')
            
    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_keezmovies = session.get('http://www.keezmovies.com/upload',proxies=proxy)

        if go_to_keezmovies.url == 'http://www.keezmovies.com/user/login':
            return False
        else:
            return True

