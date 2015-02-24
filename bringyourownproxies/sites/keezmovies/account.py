#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.account import OnlineAccount

class KeezMoviesAccount(OnlineAccount):
    
    SITE = 'KeezMovies'
    SITE_URL = 'www.keezmovies.com'
    
    def __init__(self,username,password,email,**kwargs):
        super(KeezMoviesAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_keezmovies = session.get('http://www.keezmovies.com',proxies=proxy)

        post = {"username":self.username,
                "password":self.password}
        
        session.headers.update({"X-Requested-With":"XMLHttpRequest",
                                "Accept":"application/json, text/javascript, */*; q=0.01"})
        attempt_login = session.post('http://www.keezmovies.com/ajax/login',data=post,proxies=proxy)
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

if __name__ == '__main__':
    account =  KeezMoviesAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    print account.is_logined()
