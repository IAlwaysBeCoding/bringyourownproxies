# -*- coding: utf-8 -*-
#!/usr/bin/python
import re

from bringyourownproxies.parser import VideoParser
from bringyourownproxies.errors import VideoParserError
from bringyourownproxies.sites.youporn.properties import (YouPornComment,YouPornTag,
                                                          YouPornCategory,YouPornAuthor)
__all__ = ['YouPornParser']

class YouPornParser(VideoParser):

    def get_video_stats(self,html,**kwargs):

        categories = []
        tags = []
        porn_stars = []

        document = self.etree.fromstring(html,self.parser)
        ratings = document.xpath('//div[@class="rating-count"]')[0].text.replace(' ratings)','').replace('(','')
        ratings_percentage = document.xpath('//div[@class="rating-percentage"]')[0]
        views = document.xpath('//div[@id="stats-views"]/text()')[0].replace(',','')
        uploaded_date = document.xpath('//div[@id="stats-date"]/text()')[0]
        title = document.xpath('//div[@class="container_15"]/h1[@class="grid_9"]')[0].text

        get_video_details = document.xpath('//ul[@class="info-list-content"]//a')

        for a in get_video_details:
            get_type = re.match(r'/(.*?)/(.*?)/',a.attrib['href'],re.I|re.M)
            if get_type:
                #figure out the type of data, either tag, category or porn star name
                item_type = get_type.group(1)
                if item_type == 'category':
                    #create a new YouPornCategory
                    categories.append(YouPornCategory(name=a.text,href=a.attrib['href']))
                elif item_type == 'porntags':
                    #create a new YouPornTag
                    tags.append(YouPornTag(name=a.text,href=a.attrib['href']))
                elif item_type == 'pornstar':
                    porn_stars.append((a.text,a.attrib['href']))

        video_url = document.xpath('//link[@href]/@href')[0]
        embed_code = "<iframe src={url}" \
        " frameborder=0 height=481 width=608" \
        " scrolling=no name=yp_embed_video>" \
        "</iframe>".format(url=video_url)

        author_name = document.xpath('//button[@data-name]//@data-name')[0]
        author_href = document.xpath('//div[@class="author-block--line"]//a')[0].attrib['href']
        author = YouPornAuthor(name=author_name,href=author_href)

        has_zero_comments = document.xpath('//div[@id="tab-comments"]//h2[@class="psi"]')
        if has_zero_comments:
            if has_zero_comments[0].text == 'All Comments (0)':
                total_comments = 0
        else:
            total_comments = document.xpath('//div[@id="tab-comments"]/ul/h2')[0] \
                         .text.replace('All Comments (','').replace(')','')

        has_description = document.xpath('//div[@id="videoDescription"]')
        if has_description:
            description = document.xpath('//div[@id="videoDescription"]//p')[0].text
        else:
            description = ''

        found_default_thumbnail = re.search(r'"default_thumbnail_url":"(.*?)"',html)
        if not found_default_thumbnail:
            raise VideoParserError('Cannot get thumbnail image for youporn video')

        thumbnail = found_default_thumbnail.group(1)

        found_duration_seconds = re.search(r'"duration_in_seconds":(.*?)',html)
        if not found_duration_seconds:
            raise VideoParserError('Cannot get duration in seconds for youporn video')
        duration_seconds = found_duration_seconds.group(1)

        found_duration_text = re.search(r'"duration_f":"(.*?)"',html)
        if not found_duration_text:
            raise VideoParserError('Cannot get duration text for youporn video')
        duration_text = found_duration_text.group(1)

        return {'total_comments':int(total_comments),
                'author':author,
                'porn_stars':porn_stars,
                'categories':categories,
                'tags':tags,
                'uploaded_date':uploaded_date,
                'views':views,
                'ratings':ratings,
                'ratings_percentage':ratings_percentage,
                'title':title,
                'thumbnail':thumbnail,
                'duration_seconds':duration_seconds,
                'duration_text':duration_text,
                'description':description,
                'embed_code':embed_code}

    def get_all_comments(self,html):
        comments = []
        current_page = None
        total_pages = None
        document = self.etree.fromstring(html,self.parser)

        grab_comments = document.xpath('//li')

        if len(grab_comments):
            for div in grab_comments:
                div_doc = self.etree.fromstring(self.tostring(div),self.parser)

                author = div_doc.xpath('//p[@class="name"]')[0].text
                date = div_doc.xpath('//span[@class="date"]/text()')[0].lstrip()
                text = div_doc.xpath('//p[@class="message"]/text()')[0]
                thumbs_up = int(div_doc.xpath('//div[@class="option-links"]/@data-likes')[0])
                thumbs_down = int(div_doc.xpath('//div[@class="option-links"]/@data-dislikes')[0])
                comment_id = div_doc.xpath('//div[@data-commentid]/@data-commentid')[0]

                comments.append(YouPornComment(author=author,
                                                text=text,
                                                posted_date=date,
                                                thumbs_up=thumbs_up,
                                                thumbs_down=thumbs_down,
                                                comment_id=comment_id))

            get_comments_page = document.xpath('//div[@id="watch-comment-pagination"]//div[@class="pageIndicator"]//text()')

            current_page = int(get_comments_page[1])
            total_pages = int(get_comments_page[2].replace(' of ',''))


            return (comments,current_page,total_pages)

        else:
            return (None,None,None)
    def get_download_options(self,html,**kwargs):

        options = {'720':None,
                   '480':None,
                   '240':None,
                   '180':None}

        doc = self.etree.fromstring(html,self.parser)
        download_options = doc.xpath('//ul[@class="downloadList"]/li')
        if not download_options:
            raise VideoParserError('Could not find all the video download '\
                                   'options for youporn.com video')

        for li in download_options:

            li_doc = self.etree.fromstring(self.tostring(li),self.parser)
            link = li_doc.xpath('//a')[0]

            for quality in ['/720p','/480p','/240p','/180p']:
                if quality in link.attrib['href']:
                    options[quality.replace('/','').replace('p','')] = link.attrib['href']
                    break

        return options

    def get_download_url(self,html,**kwargs):

        download_quality = kwargs.get('download_quality','default')
        download_options = self._get_download_options(html=html)
        if download_quality == 'default':

            for quality in ['720','480','240','180']:
                if download_options[quality]:
                    return download_options[quality]

            raise VideoParserError('Could not find video download url for youporn.com video')

        else:
            if download_quality in download_options:
                return download_options[download_quality]

            raise VideoParserError('Invalid download quality, only available options are 720,480,240,180 or default')

