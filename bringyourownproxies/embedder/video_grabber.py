# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
#!/usr/bin/env python
from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.embedder.errors import VideoGrabberProblem
from bringyourownproxies.embedder.sites import (youporn,motherless,
                                                drtuber,redtube,
                                                pornhub,xvideos)

SITES = {'youporn':youporn,
         'motherless':motherless,
         'drtuber':drtuber,
         'redtube':redtube,
         'pornhub':pornhub,
         'xvideos':xvideos}

class VideoGrabber(object):

    def __init__(self,http_settings=HttpSettings()):
        self.http_settings = http_settings
        self._sites = SITES

    def _go_to_video(self,url):
        session = self.http_settings.session
        proxy = self.http_settings.proxy

        for site in self._sites:
            if site in url:
                go_to_video = session.get(url,proxies=proxy)
                return (go_to_video.content,site)

        raise VideoGrabberProblem('Could not find grabber for url:{url}'.format(url=url))

    def grab_embed_code(self,url):
        go_to_video,site = self._go_to_video(url)
        return self.grab(site,go_to_video)['embed_code']

    def grab_video_stats(self,url):
        go_to_video,site = self._go_to_video(url)
        return self.grab(site,go_to_video)

    def grab_download_url(self,url,**kwargs):
        go_to_video,site = self._go_to_video(url)

        return self.grab(site,
                        go_to_video,
                        get_video_url=True,
                        get_video_stats=False,
                         **kwargs)

    def grab(self,site,html,**kwargs):

        get_video_url = kwargs.pop('get_video_url',False)
        get_video_stats = kwargs.pop('get_video_stats',True)
        download_url = None
        video_stats = None

        result = []
        if site in self._sites:
            if get_video_url :
                download_url = self._sites[site](html=html,get='download',**kwargs)
                result.append(download_url)
            if get_video_stats:
                video_stats = self._sites[site](html=html,get='stats',**kwargs)
                result.append(video_stats)

            if len(result) == 1:
                return result[0]
            else:
                return result

        raise VideoGrabberProblem('No parser available for site:{s}'.format(s=site))

if __name__ == '__main__':
    video_grabber = VideoGrabber()
    url = 'http://www.youporn.com/watch/9171547/blonde-teen-in-interracial-gangbang/'
    #url = 'http://motherless.com/FF8FFDF'
    #url = 'http://www.redtube.com/7928'
    #url = 'http://www.drtuber.com/video/2217855/katie-summers-ass-and-face-drilling-deep-by-mike-adriano'
    #url = 'http://www.pornhub.com/view_video.php?viewkey=31372320'
    #url = 'http://www.xvideos.com/video10858627/omg_big_tits_granny_really_loves_when_it_hurts'
    video_stats = video_grabber.grab_video_stats(url)
    download_url = video_grabber.grab_download_url(url,download_quality='480')
    print 'video_stats:{v}'.format(v=video_stats)
    print 'download_url:{d}'.format(d=download_url)

    #youporn_video = video_grabber.grab_embed_code(url)
    #print youporn_video
