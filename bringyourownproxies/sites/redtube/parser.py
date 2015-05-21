import urllib
import re

from bringyourownproxies.parser import VideoParser
from bringyourownproxies.errors import VideoParserError

__all__ = ['RedTubeParser']

class RedTubeParser(VideoParser):
    def _get_categories(self,html):

        categories = []
        cat_doc = self.etree.fromstring(html,self.parser)
        for link in cat_doc.xpath('//a[@title]'):
            categories.append(link.attrib['title'])

        return categories

    def _get_tags(self,html):
        tags = []
        tr_doc = self.etree.fromstring(html,self.parser)
        links = tr_doc.xpath('//td[@class="links"]/a')

        for link in links:
            tags.append(link.text)

        return tags

    def _get_views(self,html):

        tr_doc = self.etree.fromstring(html,self.parser)

        td = tr_doc.xpath('//td')[1]
        td_doc = self.etree.fromstring(self.tostring(td),self.parser)
        all_txt = td_doc.xpath('//text()')[0].strip().replace(',','')

        return all_txt

    def _get_uploaded_date(self,html):

        tr_doc = self.etree.fromstring(html,self.parser)

        td = tr_doc.xpath('//td')[1]
        td_doc = self.etree.fromstring(self.tostring(td),self.parser)
        all_txt = td_doc.xpath('//text()')[1].strip().replace('ADDED ','')

        return all_txt

    def get_video_stats(self,html):

        document = self.etree.fromstring(html,self.parser)
        details = document.xpath('//div[@class="video-details"]')
        details_doc = self.etree.fromstring(self.tostring(details[0]),self.parser)
        has_user_link = details_doc.xpath('//span[@class="linkImitation"]')

        if has_user_link:
            author = has_user_link[0].text
        else:
            author = details_doc.xpath('//a[@rel="nofollow"]')[0].text

        trs = details_doc.xpath('//table//tr')

        title = document.xpath('//h1[@class="videoTitle"]')[0].text
        categories = self._get_categories(html=self.tostring(trs[0]))
        uploaded_date = self._get_uploaded_date(html=self.tostring(trs[1]))
        views = self._get_views(html=self.tostring(trs[1]))
        tags = self._get_tags(html=self.tostring(trs[2]))

        ratings_percentage = document.xpath('//span[@class="percent-likes"]')[0].text
        thumbnail = document.xpath('//meta[@property="og:image"]/@content')[0]
        title = document.xpath('//h1[@class="videoTitle"]')[0].text
        found_video_id = re.search(r'var iVideoID = (.*?);',html)

        if not found_video_id:
            raise VideoParserError('Could not find video id for drtuber video')

        embed_code = '<iframe src=http://www.embed.redtube.com?id={video_id}' \
                    '&bgcolor=000000 width=640 height=360 frameborder=0 ' \
                    'scrolling=no></iframe>'.format(video_id=found_video_id.group(1))

        return {'author':author,
                'tags':tags,
                'categories':categories,
                'embed_code':embed_code,
                'thumbnail':thumbnail,
                'uploaded_date':uploaded_date,
                'ratings_percentage':ratings_percentage,
                'title':title,
                'views':views}


    def _get_download_options(self,html):
        find_video_options = re.search(r'{"hd":"(.*?)","480p":"(.*?)","mobile":"(.*?)",}]}',html)
        if find_video_options:
            return {'hd':find_video_options.group(1),
                    '480':find_video_options.group(2),
                    'mobile':find_video_options.group(3)}

        raise VideoParserError('Could not parse video download options for redtube.com video')

    def get_download_url(self,html,**kwargs):

        download_quality = kwargs.get('download_quality','default')
        if download_quality == 'default':
            document = self.etree.fromstring(html,self.parser)
            download_url = document.xpath('//source[@src]/@src')
            if not download_url:
                raise VideoParserError('Could not find video download url for drtuber video')

            return download_url[0]

        else:
            download_options = self._get_download_options(html=html)
            if download_quality in download_options:
                return download_options[download_quality]

            raise VideoParser('Invalid download quality, only available options are hd,480,mobile or default')

