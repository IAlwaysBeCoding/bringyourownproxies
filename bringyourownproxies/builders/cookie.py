

import json
from requests import Session
from requests.cookies import create_cookie

class CookieLoader(object):

    def load_json_to_session(self,json_cookies,session=Session()):
        _cookies = session.cookies._cookies

        for domain in json_cookies:
            _cookies[domain] = _cookies.get(domain,{})

            for path in json_cookies[domain]:
                _cookies[domain][path] = _cookies[domain].get(path,{})

                for cookie_name in json_cookies[domain][path]:
                    cookie_value = json_cookies[domain][path][cookie_name]
                    _cookies[domain][path][cookie_name] = create_cookie(name=cookie_name,
                                                                         value=cookie_value,
                                                                         path=path)

        return session

    def set_cookies_from_json(self,json_cookies_file,session=Session()):
        with open(json_cookies_file,'r') as f:
            raw_json = f.read()

        json_cookies = json.loads(raw_json)
        return self.load_json_to_session(json_cookies=json_cookies,session=session)

