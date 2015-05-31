# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
import re
import json

from requests.cookies import create_cookie

from bringyourownproxies.errors import AccountProblem,InvalidLogin,ParsingProblem
from bringyourownproxies.httpclient import HttpSettings

from bringyourownproxies.sites.account import _Account 

__all__ = ['SpankwireAccount']

class SpankwireAccount(_Account):
    
    SITE = 'Spankwire'
    SITE_URL = 'www.spankwire.com'
    
    def __init__(self,username,password,email,**kwargs):
        self.remember_me = kwargs.pop('remember_me') if kwargs.get('remember_me',False) else False
        super(SpankwireAccount,self).__init__(username=username,password=password,email=email,**kwargs)
    
    def login(self):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        
        go_to_spankwire = session.get('http://www.spankwire.com',proxies=proxy)

        doc = self.etree.fromstring(go_to_spankwire.content,self.parser)
        
        get_js_scripts = doc.xpath('//script[@type="text/javascript"]')
        login_url = None
        if get_js_scripts:
            for js in get_js_scripts:
                if js.text:
                    find_link = re.findall(r'jsUrlList.push\("(.*?)"\);',js.text,re.I|re.M)
                    if find_link:
                        if 'SpankWire2' in find_link[0]:
                            login_url = find_link[0]
                            break
        
        if login_url is None:
            raise ParsingProblem('Could not find spanwire post url to login')

        post = {"Password":str(self.password),
                "UserName":str(self.username)}
        
        session.headers.update({"X-AjaxPro-Method":"Authenticate2",
                                "Origin":"http://www.spankwire.com",
                                "Referer":"http://www.spankwire.com/"}) 
        login_url = 'http://www.spankwire.com/ajaxpro/{url}'.format(url=login_url.split('/ajaxpro/')[1])        

        attempt_login = session.post(login_url,data=json.dumps(post),proxies=proxy)
        result = attempt_login.json() 

        if 'value' in result:
            if result['value']['LoginSuccess']:
                return True
            else:
                if result['value']['Reason'] == 'Bad Username or Password':
                    raise InvalidLogin('Wrong username(email) or password')
            raise AccountProblem('Unknown problem while login into Spankwire message:{e}'.format(e=result['value']['Reason']))

    def is_logined(self):
        return self._is_logined(sign_out_xpath='//li[@id="logoutLink" and @class="display-none"]')

