# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
import re

from bringyourownproxies.parser import VideoParser
from bringyourownproxies.errors import VideoParserError

from aes import aes_decrypt_text
__all__ = ['PornhubParser']

class PornhubParser(VideoParser):

    def _get_stats_count(self,html):

        stats_doc = self.etree.fromstring(html,self.parser)
        views = stats_doc.xpath('//span[@class="count"]')[0].text.replace(',','')
        ratings_percentage = stats_doc.xpath('//span[@class="percent"]')[0].text
        thumbs_up = stats_doc.xpath('//span[@class="votesUp"]')[0].text
        thumbs_down = stats_doc.xpath('//span[@class="votesDown"]')[0].text

        return (views,ratings_percentage,thumbs_up,thumbs_down)

    def _get_porn_stars(self,html):

        porn_stars = []
        porn_doc = self.etree.fromstring(html,self.parser)
        for porn_star in porn_doc.xpath('//a[@data-id]'):
            porn_stars.append(porn_star.text.strip())

        return porn_stars

    def _get_categories(self,html):

        categories = []
        cat_doc = self.etree.fromstring(html,self.parser)
        for link in cat_doc.xpath('//a[@onclick]'):
            categories.append(link.text)

        return categories

    def _get_production_type(self,html):
        prod_doc = self.etree.fromstring(html,self.parser)
        for link in prod_doc.xpath('//a'):
            if 'video' in link.attrib['href']:
                return link.attrib['class']

    def _get_tags(self,html):
        tags = []
        tr_doc = self.etree.fromstring(html,self.parser)
        for link in tr_doc.xpath('//a'):
            tags.append(link.text)

        return tags

    def _get_uploaded_date(self,html):

        date_doc = self.etree.fromstring(html,self.parser)
        uploaded_date = date_doc.xpath('//span[@class="white"]')[0].text
        return uploaded_date

    def _get_title(self,html):

        found_title = re.search(r'video_title":"(.*?)"',html)
        if not found_title:
            raise VideoParserError('Cannot find video title in pornhub.com video')
        return found_title.group(1)

    def get_download_options(self,html,**kwargs):

        regex = '"quality_720p":"(.*?)","quality_240p":"(.*?)","quality_180p":"(.*?)","quality_480p":"(.*?)",'
        find_video_options = re.search(regex,html)
        if find_video_options:

            video_urls = []
            password = self._get_title(html=html)

            for i in xrange(1,5):
                encrypted_url = find_video_options.group(i)
                if encrypted_url:
                    video_urls.append(aes_decrypt_text(encrypted_url,password,32).decode('utf-8'))
                else:
                    video_urls.append(None)

            return {'720':video_urls[0],
                    '240':video_urls[1],
                    '180':video_urls[2],
                    '480':video_urls[3]}

        raise VideoParserError('Could not parse video download options for pornhub.com video')


    def get_video_stats(self,html):

        document = self.etree.fromstring(html,self.parser)

        thumbnail = document.xpath('//meta[@property="og:image"]/@content')[0]
        author = document.xpath('//div[@class="usernameWrap clearfix"]//a[@class="bolded"]')[0].text

        vid_row = document.xpath('//div[@class="video-info-row"]')
        pornstars = self._get_porn_stars(self.tostring(vid_row[0]))

        vid_show_less =  document.xpath('//div[@class="video-info-row showLess"]')
        categories = self._get_categories(html=self.tostring(vid_show_less[0]))
        production = self._get_production_type(html=self.tostring(vid_show_less[1]))
        tags = self._get_tags(html=self.tostring(vid_show_less[2]))
        uploaded_date = self._get_uploaded_date(html=self.tostring(vid_show_less[3]))

        stats_count = document.xpath('//div[@class="rating-info-container"]')
        views, \
        ratings_percentage, \
        thumbs_up, \
        thumbs_down = self._get_stats_count(html=self.tostring(stats_count[0]))

        found_embed_code = re.search(r'"embedCode":"(.*?)\<\\/iframe>',html)
        if not found_embed_code:
            raise VideoParserError('Cannot get embed code for pornhub.com video')

        embed_code = found_embed_code.group(1).replace('\\','').replace('"','')
        embed_code = '{e}</iframe>'.format(e=embed_code)

        found_duration = re.search(r'"video_duration":"(.*?)",',html)
        if not found_duration:
            raise VideoParserError('Cannot find video duration in pornhub.com video')

        duration_seconds = found_duration.group(1)


        title = self._get_title(html=html)
        download_options = self._get_download_options(html=html)
        options = [download_options[download] for download in download_options]

        return {'author':author,
                'tags':tags,
                'categories':categories,
                'embed_code':embed_code,
                'thumbnail':thumbnail,
                'uploaded_date':uploaded_date,
                'production':production,
                'pornstars':pornstars,
                'ratings_percentage':ratings_percentage,
                'thumbs_up':thumbs_up,
                'thumbs_down':thumbs_down,
                'title':title,
                'views':views,
                'duration_seconds':duration_seconds}


    def get_download_url(self,html,**kwargs):

        download_quality = kwargs.get('download_quality','default')
        download_options = self._get_download_options(html=html)
        if download_quality == 'default':
            for quality in ['720','480','240','180']:
                if download_options[quality]:
                    return download_options[quality]
        else:

            download_options = self._get_download_options(html=html)
            if download_quality in download_options:
                return download_options[download_quality]

            raise VideoParser('Invalid download quality, only available options are 720,480,240 or 180')

