#!/usr/bin/python
import random
import requests
from requests.packages import urllib3
urllib3.disable_warnings()

import ua_parser.user_agent_parser as ua_parser

from bringyourownproxies.errors import (MissingValidProxySettings,InvalidProxyList,
                                MissingValidUserAgentSettings,InvalidUserAgentList)

class HttpSettings(object):

    DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.2.5 (KHTML, like Gecko) Version/8.0.2 Safari/600.2.5'

    def __init__(self,**kwargs):

        user_agent = kwargs.get('user_agent',self.DEFAULT_USER_AGENT)
        proxy = kwargs.get('proxy',None)
        cookies = kwargs.get('cookies',requests.cookies.RequestsCookieJar())
        self.session = kwargs.get('session',requests.Session())

        self.user_agent = user_agent if user_agent else self.DEFAULT_USER_AGENT
        self.session.headers.update({"Connection":"Keep-alive",
                                    "Cache-Control":"no-cache",
                                    "User-Agent":user_agent})
        #validate proxy by checking it has atleast 'ip' and 'port' key inside
        self._validate_proxy(proxy=proxy)

        if proxy:
            self.proxy = self.build_proxy_settings(proxy)
        else:
            self.proxy = proxy

        if cookies:
            self.session.cookies = cookies

    def extract_cookies_from_domain(self,domain):
        #sets an empty cookie dictionary
        cookies = []
        cookie_jar = self.session.cookies
        #Get all the domains inside the cookie jar
        all_domains = cookie_jar.list_domains()
        #checks if domain starts with www
        if domain.startswith('www'):
            #make a regular domain version without 'www'
            www_domain = domain
            domain = www_domain.replace('www.','')
        else:
            #creates a 'www' domain out of the regular domain
            www_domain = 'www.{d}'.format(d=domain)

        for check_domain in [www_domain,domain]:

            if check_domain in all_domains:
                #iterate through all the cookies inside the selected domain
                for path in cookie_jar._cookies[check_domain]:
                    #Iterate through all the cookies in each path of the domain
                    for cookie_key in cookie_jar._cookies[check_domain][path]:
                        #extract cookie
                        cookie = cookie_jar._cookies[check_domain][path][cookie_key]
                        #append cookie to cookies
                        cookies.append((check_domain,path,cookie_key,cookie))

        return cookies

    def clear_cookies(self):
        self.session.cookies = requests.cookies.RequestsCookieJar()

    def change_user_agent(self,user_agent):
        self.user_agent = user_agent
        self.session.headers.update({'User-Agent':self.user_agent})

    def set_proxy(self,ip=None,port=None,username=None,password=None):
        #if ip and port equal to None, then set proxy to None
        if ip is None and port is None:
            self.proxy = None
        elif (ip is None) or (port is None):
            #if ip or port is missing, then raise exception
            raise MissingValidProxySettings('ip or port is None, cannot set proxy')
        else:
            #set new proxy
            if self.proxy is None:
                self.proxy = {}
            self.proxy['ip'] = ip
            self.proxy['port'] = port
            self.proxy['username'] = username
            self.proxy['password'] = password

            self.proxy = self.build_proxy_settings(self.proxy)

    def _validate_proxy(self,proxy):
        if proxy is not None:
            if not isinstance(proxy,dict) :
                raise MissingValidProxySettings('proxy is not a dictionary, it needs to contain ip and port keys or None')

            if ('ip' not in proxy) or ('port' not in proxy):
                raise MissingValidProxySettings('Missing ip or port in proxy dictionary')

    def build_proxy_settings(self,proxy):

        #check whether username or password exists.if it exists include it on the proxy configuration
        if proxy:
            if ('username' not in proxy) or ('password' not in proxy):
                self._validate_proxy(proxy=proxy)
                proxy_string = 'http://{ip}:{port}'.format(ip=proxy['ip'],port=proxy['port'])
            else:
                proxy_string = 'http://{username}:{password}@{ip}:{port}'.format(username=proxy['username'],
                                                                                password=proxy['password'],
                                                                                ip=proxy['ip'],
                                                                                port=proxy['port'])

            return {'http':proxy_string,
                    'https':proxy_string}

class DynamicProxySwitcher(HttpSettings):

    def __init__(self,user_agent=None,proxy=None,cookies=None,session=None,**kwargs):
        #Try to see if proxies and use_random_proxy was passed to kwargs. If it was pop them out so we can later pass them as **kwargs to super()
        proxies = kwargs.pop('proxies',None)
        use_random_proxy = kwargs.pop('use_random_proxy',False)

        if proxies is None:
            raise MissingValidProxySettings('proxies is set to None,proxies need to be a valid list containing dictionaries of proxies configuration')

        if not isinstance(proxies,list) :
            raise InvalidProxyList('proxies is not a list.It needs to have 1 or more Proxies')
        else:
            if len(proxies):
                for proxy in proxies:
                    self._validate_proxy(proxy=proxy)
            else:
                raise InvalidProxyList('proxies is an empty list.It needs to have 1 or more Proxies dictionaries')

        #set a list of internal proxies, so we can later switch between them.
        self._proxies = proxies

        #Index, to keep track of last proxy used
        self._proxy_index = 0

        self.use_random_proxy = use_random_proxy
        #if use_random_proxy is set to True, then it will start out with a random proxy from proxies,else use the first one
        if self.use_random_proxy:
            proxy = random.choice(proxies)
        else:
            proxy = proxies[0]

        super(DynamicProxySwitcher,self).__init__( user_agent=user_agent,
                                                    proxy=proxy,
                                                    cookies=cookies,
                                                    session=session,
                                                    **kwargs)

    def add_proxy(self,proxy):
        #validate proxy before adding it to the list
        self._validate_proxy(proxy=proxy)
        #add proxy to the list
        self._proxies.append(proxy)

    def remove_proxy(self,ip=None,port=None):
        if ip is None and port is None:
            #delete the last proxy in the proxy list
            del self._proxies[-1]

            #check to see if the last proxy deleted was in use
            if self._proxies.index(self.proxy):
                #if the last proxy in used is the last proxy in the list, then choose a new proxy
               self.change_proxy()
        else:
            #if an ip and port was specified, iterate through all the proxies and remove that one if found.
            for key,proxy in enumerate(self._proxies):
                if proxy['ip'] == ip and proxy['port'] == port:
                    del self._proxies[key]
                    #If the proxy selected for deletion is the current proxy in use, then change proxy
                    if self.proxy['ip'] == ip and self.proxy['port'] == port:
                        self.change_proxy()
                    break

    def change_proxy(self):

        if self.use_random_proxy:
            #set proxy to a random proxy
            found_proxy = random.choice(self._proxies)
            use_this_proxy = self._proxies.index(found_proxy)
        else:
            #Check if proxy index is using the last proxy in the list. If so, then reset index to 0
            if self._proxy_index == len(self._proxies) - 1:
                self._proxy_index = 0
            else:
                self._proxy_index += 1
            #set proxy to use to the new current proxy index
            use_this_proxy = self._proxy_index

        #validate the proxy before setting it to default
        self._validate_proxy(proxy=self._proxies[use_this_proxy])
        self.proxy = self._proxies[use_this_proxy]

class DynamicUserAgentSwitcher(HttpSettings):

    def __init__(self,user_agent=None,proxy=None,cookies=None,session=None,**kwargs):
        #Check to see if user_agents and use_random_user_agent is in kwargs,and if they are pop them or set it to None
        user_agents = kwargs.pop('user_agents',None)
        use_random_user_agent = kwargs.pop('use_random_user_agent',False)

        if user_agents is None:
            raise MissingValidUserAgentSettings('user_agents is set to None.It needs to be a list and have 1 or more User-Agents ')

        if not isinstance(user_agents,list):
            raise InvalidUserAgentList('user_agents is not a list containing User-Agents.It needs to have 1 or more User-Agents')
        else:
            if not len(user_agents):
                raise InvalidUserAgentList('user_agents is an empty list.It needs to have 1 or more User-Agents')

        #set a list of internal User-Agents, so we can later switch between them.
        self._user_agents = user_agents

        #Index, to keep track of last User-Agent used
        self._user_agent_index = 0

        self.use_random_user_agent = use_random_user_agent
        #if use_random_user_agent is set to True, then it will start out with a random User-Agent from user_agents,else use the first one
        if self.use_random_user_agent:
            user_agent = random.choice(user_agents)
        else:
            user_agent = user_agents[0]

        super(DynamicUserAgentSwitcher,self).__init__( user_agent=user_agent,
                                proxy=proxy,
                                cookies=cookies,
                                session=session,
                                **kwargs)

    def add_user_agent(self,user_agent):
        #add User-Agent to the list
        self._user_agents.append(user_agent)

    def remove_user_agent(self,user_agent=None):

        if user_agent is None:
            #check to see if the last User-Agent deleted was in use
            if self._user_agents.index(self.user_agent) == len(self._user_agents)-1:
                #delete the last User-Agent in the user-agent list
                del self._user_agents[-1]
                #if the last User-Agent was in use, then get a new User-Agent
                self.get_new_user_agent()
            else:
                #delete the last User-Agent in the user-agent list
                del self._user_agents[-1]

        if user_agent in self._user_agents:
            #delete the found User-Agent from the list
            del self._user_agents[self._user_agents.index(user_agent)]
            #If the deleted User-Agent was in use, then select a new one
            if user_agent == self.user_agent:
                self.get_new_user_agent()

    def get_new_user_agent(self):
        if self.use_random_user_agent:
            #set user_agent to a random User-Agent
            found_user_agent = random.choice(self._user_agents)
            use_this_user_agent = self._user_agents.index(found_user_agent)
        else:
            #Check if user_agent index is using the last User-Agent in the list. If so, then reset index to 0
            if self._user_agent_index == len(self._user_agents) - 1:
                self._user_agent_index = 0
            else:
                self._user_agent_index += 1
            #set user_agent to use to the new current user_agent index
            use_this_user_agent = self._user_agent_index

        self.user_agent = self._user_agents[use_this_user_agent]
        #update the new User-Agent to the session
        self.session.headers.update({'User-Agent':self.user_agent})

class DynamicUserAgentProxySwitcher(DynamicProxySwitcher,DynamicUserAgentSwitcher):

    def __init__(self,user_agent=None,proxy=None,cookies=None,session=requests.Session(),**kwargs):

        #Set the default proxy settings
        proxies = kwargs.pop('proxies',None)
        use_random_proxy = kwargs.pop('use_random_proxy',False)

        #Set the default User-Agent settings
        user_agents = kwargs.pop('user_agents',None)
        use_random_user_agent = kwargs.pop('use_random_user_agent',False)

        super(DynamicUserAgentProxySwitcher,self).__init__(user_agent=user_agent,
                                                            proxy=proxy,
                                                            cookies=cookies,
                                                            session=session,
                                                            proxies=proxies,
                                                            use_random_proxy=use_random_proxy,
                                                            user_agents=user_agents,
                                                            use_random_user_agent=use_random_user_agent,
                                                            **kwargs)

if __name__ == '__main__':
    proxies = [{'ip':'127.0.0.1','port':'8888','username':'test','password':'testpassword'},
            {'ip':'127.0.0.1','port':'8889','username':'test','password':'testpassword'},
            {'ip':'127.0.0.1','port':'8890','username':'test','password':'testpassword'}]
    user_agents = ['ua1','ua2','ua3','ua4','ua5']
    http = DynamicProxySwitcher(proxies=proxies,use_random_proxy=True)
    #ua = DynamicUserAgentSwitcher(user_agents=user_agents,use_random_user_agent=True)
    multi = DynamicUserAgentProxySwitcher(user_agents=user_agents,proxies=proxies,use_random_user_agent=True)
    hit = multi.session.get('http://blackhatworld.com')

    cookie_jar = multi.session.cookies
    print cookie_jar
#    print vars(cookie_jar)
#    print dir(cookie_jar)
    print multi.extract_cookies_from_domain('blackhatworld.com')
    print 'done'
