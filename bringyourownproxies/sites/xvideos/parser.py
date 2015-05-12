import urllib
import re

from bringyourownproxies.parser import VideoParser
from bringyourownproxies.errors import VideoParserError

__all__ = ['XvideosVideoParser']
class XvideosVideoParser(VideoParser):

    def get_video_stats(self,html):
        tags = []

        document = self.etree.fromstring(html,self.parser)
        ratings = document.xpath('//span[@id="ratingTotal"]')[0].text
        ratings_percentage = document.xpath('//span[@id="rating"]')[0].text.replace('%','')
        views = document.xpath('//span[@class="nb_views"]')[0].text.replace(',','').strip().replace('"','')
        video_duration = document.xpath('//span[@class="duration"]')[0].text.replace('- ','')
        author_name = document.xpath('//li[@class="profile_name"]/a')[0].text
        author_href = document.xpath('//li[@class="profile_name"]/a')[0].attrib['href']
        total_comments =document.xpath('//span[@class="nbVideoComments"]')[0].text

        for a in document.xpath('//a[@href]'):
            if a.attrib['href'].startswith('/tags/'):
                if a.text:
                    tags.append(a.text)

        return {'total_comments':int(total_comments),
                'author':author_name,
                'author_url':'http://www.xvideos.com{url}'.format(url=author_href),
                'tags':tags,
                'views':views,
                'video_duration':video_duration,
                'ratings':ratings,
                'ratings_percentage':ratings_percentage}

    def get_download_url(self,html):

        found_flv_url = re.search(r'flv_url=(.*?)\&amp;',html)
        if not found_flv_url:
            raise VideoParserError('Missing video download url for xvideos video')
        return urllib.unquote_plus(found_flv_url.group(1))

