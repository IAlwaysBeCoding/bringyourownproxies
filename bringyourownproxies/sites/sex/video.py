#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

import path
from bringyourownproxies.video import (OnlineVideo,VideoParser,VideoUploadRequest,
                                        VideoUploaded,Tag,Title)
from bringyourownproxies.errors import (InvalidVideoUrl,InvalidVideoParser)
from bringyourownproxies.utils import show_printable_chars

from errors import CouldNotParseFramePinUlr
from comment import SexComment
from board import SexBoard


class SexTag(Tag):
    SITE = 'Sex'
    SITE_URL = 'www.sex.com'

    def __init__(self,name,**kwargs):
        self.href = kwargs.pop('href') if kwargs.get('href',False) else None

        super(SexTag,self).__init__(name=name,**kwargs)

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
                print self.tostring(possible_pin_button)
                likes = int(possible_pin_button.text.replace(',',''))
                break

        repins = None 
        
        find_repin_button = doc.xpath('//a[@class="btn btn-danger"]')
        for possible_pin_button in find_repin_button:
            if 'video/' in possible_pin_button.attrib['href']:
                print self.tostring(possible_pin_button)
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
        
class SexVideoPinRequest(VideoUploadRequest):
    
    def __init__(self,video_file,title,tags,board,**kwargs):
        self.board = board
        self.sex_tags = kwargs.pop('sex_tags') if kwargs.get('sex_tags',False) else []
        
        
        super(SexVideoPinRequest,self).__init__(video_file=video_file,
                                                title=title,
                                                tags=tags,
                                                **kwargs)
                                

    def __repr__(self):

        return "<Sex VideoPin Request title:{title} tags:{tags}" \
            " board:{board}>".format(title=self.title.name,
                                                tags=",".join([t.name for t in self.tags]),
                                                board=self.board.name)

class SexVideoPin(OnlineVideo):
    SITE = 'Sex'
    SITE_URL = 'www.sex.com'
    def __init__(self,url=None,title=None,category=None,**kwargs):
        self.pin_id = kwargs.pop('pin_id') if kwargs.get('pin_id',False) else None
        self.sex_parser = kwargs.pop('sex_parser') if kwargs.get('sex_parser',False) else SexParser()
        self.pinned_date = kwargs.pop('pinned_date') if kwargs.get('pinned_date',False) else None
        self.author = kwargs.pop('author') if kwargs.get('author',False) else None
        self.tags = kwargs.pop('tags') if kwargs.get('tags',False) else None
        self.total_comments = kwargs.pop('total_comments') if kwargs.get('total_comments',False) else None
    
        if type(self.sex_parser) != SexParser:
            raise InvalidVideoParser('parser is not a valid SexParser')
        
        super(SexVideoPin,self).__init__(url=url,title=title,category=category,**kwargs)
        
    def _get_video_id(self):

        find_video_id = re.match(r'(.*?)/watch/(.*?)/(.*?)',self.url,re.I|re.M)
        if find_video_id:
            return find_video_id.group(2)

    def download(self,**kwargs):
        dir_to_save = kwargs.get('dir_to_save',None)
        name_to_save_as = kwargs.get('name_to_save_as',None)
        video_file = kwargs.get('video_file',0)
        try:
            #verify download dir and file name
            saving_path,filename = self._verify_download_dir(dir_to_save,name_to_save_as)
                    
            go_to_video = self.go_to_video()
            session = self.http_settings.session
            proxy = self.http_settings.proxy
            #grab the raw download url to the video source
            frame_url = self.sex_parser.get_frame_url(go_to_video)
            go_to_video_source = session.get(frame_url,proxies=proxy)
            
            video_url = self.sex_parser.get_video_pin_url(go_to_video_source.content)
            if type(video_url) == tuple or type(video_url) == list:
                download_video = session.get(video_url[video_file],proxies=proxy)
            else:
                download_video = session.get(video_url,proxies=proxy)
            
            #create a new file path to where we will save the downloaded movie
            save_at = path.Path.joinpath(saving_path,filename)
            
            with open(save_at.abspath(),'w+') as f:
                f.write(download_video.content)
        except Exception as exc:
            self.on_failed_download(exception=exc)
            raise exc
        else:
            self.on_success_download(video_url=video_url,video_location=save_at.abspath())

    def get_video_info(self):
        
        go_to_video = self.go_to_video()
        stats = self.sex_parser.get_video_stats(go_to_video)
        return stats
    
    def get_comments_from_page(self,page):

        session = self.http_settings.session 
        proxy = self.http_settings.proxy

    def get_comments(self,start_page=1,end_page=0):
        pass


if __name__ ==  '__main__':
    video = SexVideoPin(url='http://www.sex.com/video/12810676-petplay-video/')
    print video.get_video_info()
    #video.download()