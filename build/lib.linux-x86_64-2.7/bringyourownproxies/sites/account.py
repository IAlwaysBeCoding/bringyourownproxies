#!/usr/bin/python
import json 

from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.errors import InvalidLogin,AccountProblem
from bringyourownproxies.account import OnlineAccount

from bringyourownproxies.sites.errors import CouldNotFindVar

ERROR_MESSAGES_XPATH = ['//div[@class="message_error"]/text()']
WRONG_USER_PASSWORD_MESSAGES = ['Invalid Username or Password. Username and Password are case-sensitive.',
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
        error_msg_xpath = kwargs.get('error_msg_xpath',None)
        wrong_pass_msg = kwargs.get('wrong_pass_msg',None)
        html = response.content
        
        doc = self.etree.fromstring(html,self.parser)
        

        if error_msg_xpath:
            xpath_error = doc.xpath(error_msg_xpath)
            if xpath_error:
                error_msg = xpath_error[0]
                
                if wrong_pass_msg:
                    self._check_for_wrong_pass(error_msgs = [wrong_pass_msg])
                else:
                    self._check_for_wrong_pass(error_msgs = WRONG_USER_PASSWORD_MESSAGES)

                raise AccountProblem('Something went wrong ' \
                                    ' while login into {site}' \
                                    ' username:{username} ' \
                                    ' password:{password} ' \
                                    ' email:{email}'.format(site=self.SITE,
                                                            username=self.username,
                                                            password=self.password,
                                                            email=self.email))
                    
        else:
            
            for xpath in ERROR_MESSAGES_XPATH:
                current_xpath = doc.xpath(xpath)
                if current_xpath:
        
                    error_msg = current_xpath[0]
                    
                    if wrong_pass_msg:
                        self._check_for_wrong_pass(error_msgs = [wrong_pass_msg])
                    else:
                        self._check_for_wrong_pass(error_msgs = WRONG_USER_PASSWORD_MESSAGES)

                    raise AccountProblem('Something went wrong ' \
                                        ' while login into {site}' \
                                        ' username:{username} ' \
                                        ' password:{password} ' \
                                        ' email:{email}'.format(site=self.SITE,
                                                                username=self.username,
                                                                password=self.password,
                                                                email=self.email))

    def _check_for_wrong_pass(self,**kwargs):
        error_msgs = kwargs.get('error_msgs',WRONG_USER_PASSWORD_MESSAGES)
        
        for error in error_msgs:
            if error_msg.strip() == error:
                raise InvalidLogin('Wrong username or password')

            else:
                raise AccountProblem('Something went wrong ' \
                                        ' while login into msg:{msg}'\
                                        '{site}' \
                                        ' username:{username} ' \
                                        ' password:{password} ' \
                                        ' email:{email}'.format(site=self.SITE,
                                                                msg=error_msg.strip(),
                                                                username=self.username,
                                                                password=self.password,
                                                                email=self.email))
                                                                
