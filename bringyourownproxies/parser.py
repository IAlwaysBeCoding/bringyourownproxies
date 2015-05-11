from lxml import etree
from lxml.etree import HTMLParser,tostring

class VideoParser(object):
    parser = HTMLParser()
    etree = etree
    tostring = tostring
    def get_video_stats(self,html):
        raise NotImplementedError('get_stats not implemented, this function returns the video stats like ratings, views, video length, author etc.')
    def get_download_url(self,html):
        raise NotImplementedError('get_download_url not implemented, this function should return the raw url video url to the current video')


