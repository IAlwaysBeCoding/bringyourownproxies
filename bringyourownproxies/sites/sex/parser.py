# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
import re

from bringyourownproxies.parser import VideoParser
from bringyourownproxies.sites.sex.errors import CouldNotParseFramePinUlr
from bringyourownproxies.sites.sex.properties import SexTag,SexComment

__all__ = ['SexParser']

class SexParser(VideoParser):

    def get_frame_url(self,html):

        doc = self.etree.fromstring(html,self.parser)
        for frame in doc.xpath('//iframe'):

            if 'embed' in frame.attrib['src']:
                frame_url = "http://sex.com{frame}".format(frame=frame.attrib['src'])
                return frame_url

        raise CouldNotParseFramePinUlr('Could not retrieve frame url')

    def get_video_pin_url(self,html):

        sources = []
        find = re.findall(r'file: "(.*?)",',html,re.I|re.M)
        if find:
            for f in find:
                if 'http:' in f:
                    sources.append(f)
        return sources

    def get_video_stats(self,html):

        doc = self.etree.fromstring(html,self.parser)

        author = doc.xpath('//span[@itemprop="author"]')[0].text
        total_comments = doc.xpath('//h2[@class="pull-left"]/text()')[0].\
                        strip().\
                        replace('Comments (','').\
                        replace(')','')
        tags = []
        get_tags = doc.xpath('//div[@class="tags"]/a')
        for t in get_tags:
            tags.append(SexTag(name=t.text,href=t.attrib['href']))

        comments = []
        any_comments = doc.xpath('//div[@class="comments"]')
        if any_comments:
            comments_doc = self.etree.fromstring(self.tostring(any_comments[0]),self.parser)
            for comment in comments_doc.xpath('//div[@class="comment"]'):
                current_comment_doc = self.etree.fromstring(self.tostring(comment),self.parser)
                avatar_url = current_comment_doc.xpath('//div[@class="picture"]/img')[0].attrib['src']
                author = current_comment_doc.xpath('//a[@class="commentUsername"]')[0].text
                author_href = current_comment_doc.xpath('//a[@class="commentUsername"]/@href')[0]
                comment_text = current_comment_doc.xpath('//div[@class="text"]/text()')[1].strip()

                comments.append(SexComment(author=author,
                                            text=comment_text,
                                            author_avatar=avatar_url,
                                            author_href=author_href))

        uploaded_date = doc.xpath('//time[@itemprop="uploadDate"]')[0].attrib['datetime']
        exact_uploaded_date = doc.xpath('//time[@itemprop="uploadDate"]')[0].text

        likes = None

        find_pin_likes_button = doc.xpath('//a[@class="btn"]')
        for possible_pin_button in find_pin_likes_button:
            if 'video/' in possible_pin_button.attrib['href']:
                likes = int(possible_pin_button.text.replace(',',''))
                break

        repins = None

        find_repin_button = doc.xpath('//a[@class="btn btn-danger"]')
        for possible_pin_button in find_repin_button:
            if 'video/' in possible_pin_button.attrib['href']:
                repins = int(possible_pin_button.text.replace(',',''))
                break

        return {'author':author,
                'repins':repins,
                'likes':likes,
                'tags':tags,
                'uploaded_date':uploaded_date,
                'exact_uploaded_date':exact_uploaded_date,
                'comments':comments,
                'total_comments':int(total_comments)}

