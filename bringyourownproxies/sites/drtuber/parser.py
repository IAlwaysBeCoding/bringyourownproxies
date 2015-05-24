import urllib
import re

from bringyourownproxies.parser import VideoParser
from bringyourownproxies.errors import VideoParserError

__all__ = ['DrTuberParser']

class DrTuberParser(VideoParser):
    def _get_categories(self,html):

        categories = []
        cat_doc = self.etree.fromstring(html,self.parser)
        for link in cat_doc.xpath('//a'):
            categories.append(link.text)

        return categories

    def get_video_stats(self,html,**kwargs):

        document = self.etree.fromstring(html,self.parser)
        title = document.xpath('//p[@class="title_substrate"]')[0].text
        author = document.xpath('//span[@class="autor text_t"]/a[@href]')[0].text

        uploaded_date = document.xpath('//span[@class="autor text_t"]//text()')[2].strip()

        website = document.xpath('//span[@class="autor_web"]/a[@href]')[0]. \
                    attrib['href'].replace('/user_site_out.php?link=','')
        website = urllib.unquote(website)

        c_list = document.xpath('//div[@class="categories_list"]')[0]
        categories = self._get_categories(html=self.tostring(c_list))

        thumbnail = document.xpath('//video[@controls="controls"]/@poster')[0]
        found_video_id = re.search(r'var video_id = "(.*?)"',html)

        if not found_video_id:
            raise VideoParserError('Could not find video id for drtuber video')

        embed_code = '<iframe src=http://www.drtuber.com/embed/{video_id}' \
                    ' width=608 height=454 frameborder=0 ' \
                    ' scrolling=no></iframe>'.format(video_id=found_video_id.group(1))

        return {'author':author,
                'categories':categories,
                'embed_code':embed_code,
                'thumbnail':thumbnail,
                'uploaded_date':uploaded_date,
                'title':title}

    def get_download_url(self,html,**kwargs):

        document = self.etree.fromstring(html,self.parser)
        download_url = document.xpath('//source[@src]/@src')
        if not download_url:
            raise VideoParserError('Could not find video download url for drtuber video')

        return download_url[0]
