# -*- coding: utf-8 -*-
#!/usr/bin/python

from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.httpclient import HttpSettings

def youporn(html):
    doc = etree.fromstring(html,HTMLParser())
    url = doc.xpath('//link[@href]/@href')[0]

    embed_code = "<iframe src={url}" \
    " frameborder=0 height='481' width='608'" \
    " scrolling=no name='yp_embed_video'>" \
    "</iframe>".format(url=url)
    return {'embed_code':embed_code}

def xvideos(html):
    pass
class VideoGrabber(object):

    def __init__(self,http_settings=HttpSettings()):
        self.http_settings = http_settings
        self._sites = {'youporn':youporn,
                       'xvideos':xvideos}
    def grab_embed_code(self,url):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        if 'youporn.com' in url:
            go_to_video = session.get(url,proxies=proxy)
            return self.grab('youporn',go_to_video.content)
        else:
            pass

    def grab(self,site,html):
        if site == 'youporn':
            return self._sites['youporn'](html)


if __name__ == '__main__':
    grabber = VideoGrabber()
    print grabber.grab_embed_code('http://www.youporn.com/watch/9750523/hot-emma-stoned-porn-debut/')







