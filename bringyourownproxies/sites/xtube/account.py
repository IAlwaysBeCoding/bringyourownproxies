# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.errors import AccountProblem,InvalidLogin,CaptchaRequired
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

__all__ = ['XtubeAccount']

class XtubeAccount(_Account):
    
    SITE = 'Xtube'
    SITE_URL = 'www.xtube.com'
    RECAPTCHA_KEY = '6Ld65scSAAAAAGLEbFoUl8hyXh40S4YEa6i1weN_'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(XtubeAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self,**kwargs):
        
        '''
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_xtube = session.get('http://www.xtube.com',proxies=proxy)
        go_to_login = session.get('http://www.xtube.com/login.php',proxies=proxy)
        with open('test1_login.html','w+') as f:
            f.write(go_to_login.content)
        
        doc = self.etree.fromstring(go_to_xtube.content,self.parser)
        get_url = doc.xpath('//input[@type="hidden" and @name="url"]/@value')[0]
        get_time = doc.xpath('//input[@type="hidden" and @name="time"]/@value')[0]
        get_hash  = doc.xpath('//input[@type="hidden" and @name="hash"]/@value')[0]

        post = {"remember_me":"1" if self.remember_me else "0",
                "url":get_url,
                "time":get_time,
                "hash":get_hash,
                "user_id":self.username,
                "password":self.password,
                "remember_me":"on" if self.remember_me else "off"}
                
        print post
        session.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'})
        
        attempt_login = session.post('http://www.xtube.com/login_process.php',data=post,proxies=proxy)
        '''
        attempt_login  = self._login(username="user_id",
                                    extra_post_vars={"remember_me": "1" if self.remember_me else "0"},
                                    before_post_url_vars={"url":None,
                                                        "time":None,
                                                        "hash":None},
                                    before_post_url='http://www.xtube.com/login.php',
                                    post_url='http://www.xtube.com/login_process.php')



        doc = self.etree.fromstring(attempt_login.content,self.parser)
        with open('test_login.html','w+') as f:
            f.write(attempt_login.content)
        
        
        
        if doc.xpath('//a[@class="Masthead__user__label Masthead__user__label__log" and @href="/logout.php"]'):
            return True
        else:
            get_error_msg = doc.xpath('//div[@class="loginMessage color_red"]/text()')
            if get_error_msg[0].strip() == "The reCAPTCHA wasn't entered correctly":
                raise CaptchaRequired('reCaptcha is required to login into Xtube')
            print get_error_msg[0].strip()
            
        '''
        recaptcha_challenge_field
            if get_error_msg:
                if get_error_msg[0].text == 'Invalid Username or Password. Username and Password are case-sensitive.':
                    raise InvalidLogin('Wrong username or password')
        raise AccountProblem('Unknown problem while login into Xtube')
        '''

    def is_logined(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_Xtube = session.get('http://www.xtube.com/',proxies=proxy)

        doc = self.etree.fromstring(go_to_Xtube.content,self.parser)
        is_sign_out_link = doc.xpath('//a[@class="logout" and @title="Logout"]')
        if is_sign_out_link:
            return True
        else:
            return False

