#!/usr/bin/python
import json 

from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.errors import InvalidLogin,AccountProblem
from bringyourownproxies.account import OnlineAccount

from bringyourownproxies.sites.errors import CouldNotFindVar

ERROR_MESSAGES_XPATH = ['//div[@class="message_error"]/text()']
WRONG_PASSWORD_MESSAGES = ['Invalid Username or Password. Username and Password are case-sensitive.',
                                '! Invalid Username or Password. Username and Password are case-sensitive.'] 
                                
SIGN_OUT_XPATH = ['//li[@class="logout"]','//a[@href="/sign-out/"]']
JSON_SUCCESS_KEY = []
JSON_ERROR_KEY = []
JSON_ERROR_MESSAGES_KEY = []


class _Account(OnlineAccount):

    def _login(self,**kwargs):
        
        username = kwargs.get('username','username')
        password = kwargs.get('password','password')
        email = kwargs.get('email',self.email)
        ajax = kwargs.get('ajax',False)
        extra_headers = kwargs.get('extra_headers',{})
        before_post_url = kwargs.get('before_post_url',None)
        before_post_url_vars = kwargs.get('before_post_url_vars',{})
        post_url = kwargs.get('post_url',None)
        post_url_vars = kwargs.get('post_url_vars',{})
        extra_post_vars = kwargs.get('extra_post_vars',{})
        post_vars = kwargs.get('post_vars',{username:self.username,password:self.password})

        session = self.http_settings.session
        proxy = self.http_settings.proxy
        

        if not self.SITE_URL.startswith('http://') or \
            not self.SITE_URL.startswith('https://'):
            domain_url = 'http://{url}'.format(url=self.SITE_URL)

        go_to_site = session.get(domain_url,proxies=proxy)
        
        if before_post_url:

            before_posting_url = session.get(before_post_url,proxies=proxy)
            
            doc = self.etree.fromstring(before_posting_url.content,self.parser)
            for var in before_post_url_vars:
                if before_post_url_vars[var] is None:
                    get_var = doc.xpath('//input[@name="{name}"]'.format(name=var))
                    if get_var:
                        post_vars[var] = get_var[0].attrib['value']
                    else:
                        raise CouldNotFindVar('Could not find {v} in url:{u}'.format(v=var))
                else:
                    post_vars[var] = before_post_url_vars[var]
        
        
        if ajax:
            session.headers.update({"X-Requested-With":"XMLHttpRequest"})
        
        for extra in extra_post_vars:
            post_vars[extra] = extra_post_vars[extra]

        for header in extra_headers:
            session.headers[header] = extra_headers[header]
        
        attempt_login = session.post(post_url,data=post_vars,proxies=proxy)

        return attempt_login
            
    
    def _find_sign_out(self,response,**kwargs):
        
        sign_out_xpath = kwargs.get('sign_out_xpath',None)
        
        html = response.content
        doc = self.etree.fromstring(html,self.parser)
        
        found = False
        if sign_out_xpath:
            if doc.xpath(sign_out_xpath):
                found = True
        else:
            for xpath in SIGN_OUT_XPATH:
                if doc.xpath(xpath):
                    found = True
                    break

        return found
        

    def _is_logined(self,**kwargs):
        
        session = self.http_settings.session
        proxy = self.http_settings.proxy 
        
        if not self.SITE_URL.startswith('http://') or \
            not self.SITE_URL.startswith('https://'):
            domain_url = 'http://{url}'.format(url=self.SITE_URL)
        go_to_site = session.get(domain_url,proxies=proxy)
        
        is_signed_in = self._find_sign_out(go_to_site,**kwargs)
        
        return is_signed_in
    
    def _find_login_errors(self,response,**kwargs):
        error_msg_xpath = kwargs.get('error_msg_xpath',ERROR_MESSAGES_XPATH)
        wrong_pass_msg = kwargs.get('wrong_pass_msg',WRONG_PASSWORD_MESSAGES)
        use_username = kwargs.get('use_username',True)
        use_password = kwargs.get('use_password',True)

        doc = self.etree.fromstring(response.content,self.parser)
        
        if not isinstance(error_msg_xpath,(list,tuple)):
                error_msg_xpath = [error_msg_xpath]

        if not isinstance(wrong_pass_msg,(list,tuple)):
                wrong_pass_msg = [wrong_pass_msg]

                
        for xpath in error_msg_xpath:
            xpath_error = doc.xpath(xpath)
            
            if xpath_error:
                error_msg = xpath_error[0]
                has_wrong_pass = self._is_wrong_password(error=error_msg,look_in_these=wrong_pass_msg)

                if has_wrong_pass:
                    raise InvalidLogin('Wrong username(email) or password')
                    
                raise AccountProblem('Error:{error} ' \
                                    ' while login into {site}' \
                                    ' username:{username} ' \
                                    ' password:{password} ' \
                                    ' email:{email}'.format(error=error_msg,
                                                            site=self.SITE,
                                                            username=self.username,
                                                            password=self.password,
                                                            email=self.email))

    def _is_wrong_password(self,error,**kwargs):
        look_in_these = kwargs.get('look_in_these',WRONG_PASSWORD_MESSAGES)
        if not isinstance(look_in_these,(list,tuple)):
            messages_to_match = [look_in_these]
            
        else:
            if isinstance(look_in_these,(list,tuple)):
                messages_to_match = look_in_these
            else:
                raise TypeError('look_in_these needs to be a list,tuple or a str containing the wrong msg password to look for')    


        for match in messages_to_match:
            if match.strip() == error.strip():
                return True
                break
                
        return False

