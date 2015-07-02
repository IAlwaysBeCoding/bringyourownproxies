
from bringyourownproxies.account import OnlineAccount
from bringyourownproxies.video import VideoUploadRequest
from bringyourownproxies.sites.upload import _Upload

from cookieloader import CookieLoader

from mrq.task import Task


class UploadVideoException(Exception):
    pass


class UploadVideo(Task):

    cookie_loader = CookieLoader()
    '''
    tag_builder = TagBuilder()
    category_builder = CategoryBuilder()
    title_builder = TitleBuilder()
    description_builder = DescriptionBuilder()
    '''
    def run(self,params):

        self.class_upload = params.get('class_upload',_Upload)
        self.class_account = params.get('class_account',OnlineAccount)
        self.class_video_request = params.get('class_video_request',VideoUploadRequest)
        self.video_url = params.get('video_url',None)
        self.video_categories = params.get('categories',None)
        self.video_title = params.get('title',None)
        self.video_tags = params.get('tags',None)
        self.video_description = params.get('description',None)
        self.account_username = params.get('username',None)
        self.account_password = params.get('password',None)
        self.account_email = params.get('email',None)
        self.account_cookies = params.get('cookies',None)
        self.proxy_username = params.get('proxy_username',None)
        self.proxy_password = params.get('proxy_password',None)
        self.proxy_port = params.get('proxy_port',None)
        self.proxy_ip = params.get('proxy_ip',None)
        self.redis_host = params.get('redis_host',None)
        self.redis_port = params.get('redis_port',None)
        self.redis_db = params.get('redis_db',None)
        self.option_use_proxies = params.get('use_proxies',True)
        self.option_use_redis = params.get('save_redis',True)
        self.option_use_cookies = params.get('use_cookies',True)
        self.option_save_cookies = params.get('save_cookies',True)

        self.site_account = self.class_account(username=self.account_username,
                                password=self.account_password,
                                email=self.account_email)

    def verify_account_works(self):

        if not self.option_use_cookies:
            self.site_account.login()

            if not self.site_account.is_logined():
                raise UploadVideoException('Could not logged in successfully' \
                                           ' at {url}'. \
                                           format(url=self.site_account.SITE_URL))
        else:
            if self.account_cookies:
                _session = self.account_cookies.http_settings.session
                self.cookie_loader.set_cookies_from_json(json_cookies_file=self.account_cookies,
                                                        session=_session)

            if not self.site_account.is_logined():
                self.site_account.login()

                if not self.site_account.is_logined():
                    raise UploadVideoException('Cookies were invalid and ' \
                                               'could not logged in successfully' \
                                               ' at {url}'. \
                                               format(url=self.site_account.SITE_URL))

    def load_cookies_from_json(self,json_file,session):
        session = self.cookie_loader.from_json(json_file,session=Session())
        return session.cookies._cookies


if __name__ == '__main__':
    import requests
    from cookies import Cookies,Cookie
    from cookielib import Cookie
    from bringyourownproxies.sites import YouPornAccount
    username = 'tedwantsmore'
    password = 'money1003'
    #youporn_account.login()
    #youporn_account.save_cookies('/root/Dropbox/youporn_cookies.txt')
    #youporn_account.load_cookies('/root/Dropbox/youporn_cookies.txt')
    print youporn_account.is_logined()
    http_settings = youporn_account.http_settings
    a_s = http_settings.session
    cookie_loader = CookieLoader()
    s = requests.Session()
    #s.get('http://www.youporn.com')

    cookie_loader = CookieLoader()
    cookie_loader.set_cookies_from_json(json_cookies_file='/root/Dropbox/youporn_cookies.txt',session=a_s)

    print '************************'
    #print s.cookies._cookies
    print '************************'
    print youporn_account.http_settings.session.cookies._cookies
    with open('/root/Dropbox/youporn_logged_in.html','w+') as f:
        f.write(s.get('http://www.youporn.com').content)

    print youporn_account.is_logined()


