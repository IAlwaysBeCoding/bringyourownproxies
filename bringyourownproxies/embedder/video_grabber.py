from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.embedder.errors import VideoGrabberProblem
from bringyourownproxies.embedder.sites import youporn

SITES = {'youporn':youporn}

print youporn
class VideoGrabber(object):

    def __init__(self,http_settings=HttpSettings()):
        self.http_settings = http_settings
        self._sites = SITES

    def grab_embed_code(self,url):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        for site in self._sites:
            if site in url:
                go_to_video = session.get(url,proxies=proxy)
                return self.grab(site,go_to_video.content)['embed_code']

        raise VideoGrabberProblem('Could not find grabber for url:{url}'.format(url=url))

    def grab(self,site,html):
        if site in self._sites:
            return self._sites[site](html=html)

        raise VideoGrabberProblem('No parser available for site:{s}'.format(s=site))

if __name__ == '__main__':
    video_grabber = VideoGrabber()
    url = 'http://www.youporn.com/watch/9171547/blonde-teen-in-interracial-gangbang/'
    youporn_video = video_grabber.grab_embed_code(url)
    print youporn_video

