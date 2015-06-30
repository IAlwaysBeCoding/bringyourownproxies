# -*- coding: utf-8 -*-
#!/usr/bin/python
import re
import sys
import traceback

import path

from bringyourownproxies.video import OnlineVideo,VideoUploadRequest,VideoUploaded
from bringyourownproxies.errors import (InvalidVideoUrl,InvalidVideoParser,InvalidTag,
                                        InvalidCategory,InvalidTitle,InvalidDescription)

from bringyourownproxies.sites.youporn.parser import YouPornParser
from bringyourownproxies.sites.youporn.properties import (YouPornTag,YouPornCategory,YouPornDescription,
                                                        YouPornTitle)

__all__ = ['YouPornVideo','YouPornVideoUploadRequest','YouPornVideoUploaded']

class YouPornVideo(OnlineVideo):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,title=None,category=None,**kwargs):

        self.url = kwargs.pop('url',None)
        self.video_id = kwargs.pop('video_id',self._get_video_id())
        self.video_parser = kwargs.pop('video_parser',YouPornParser())
        self.ratings = kwargs.pop('ratings',None)
        self.ratings_percentage = kwargs.pop('ratings_percentage',None)
        self.views = kwargs.pop('views',None)
        self.uploaded_date = kwargs.pop('uploaded_date',None)
        self.categories = kwargs.pop('categories',None)
        self.tags = kwargs.pop('tags',None)
        self.author = kwargs.pop('author',None)
        self.porn_stars = kwargs.pop('porn_stars',None)
        self.total_comments = kwargs.pop('total_comments',None)

        if not isinstance(self.video_parser,YouPornParser):
            raise InvalidVideoParser('parser is not a valid YouPornParser')

        super(YouPornVideo,self).__init__(title=title,
                                        category=category,
                                        url=self.url,
                                        video_id=self.video_id,
                                        **kwargs)

    def _get_video_id(self):

        find_video_id = re.match(r'(.*?)/watch/(.*?)/(.*?)',self.url,re.I|re.M)
        if find_video_id:
            return find_video_id.group(2)

    def go_to_video(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        #check that the video url belongs to a Youporn.com video, else raise an error.
        if self.SITE_URL not in self.url:
            raise InvalidVideoUrl('Invalid video url, video does not belong to YouPorn.com')

        video = session.get(self.url,proxies=proxy)
        return video.content

    def download(self,name_to_save_as=None):

        try:

            saving_path,filename = self._verify_download_dir(name_to_save_as)
            save_at = path.Path.joinpath(saving_path,filename)

            go_to_video = self.go_to_video()
            video_url = self.video_parser.get_download_url(go_to_video)
            self._download(video_url,name_to_save_as)

        except Exception as exc:

            self.call_hook('failed',video_url=self.url,
                                    http_settings=self.http_settings,
                                    name_to_save_as=name_to_save_as,
                                    traceback=traceback.format_exc(),
                                    exc_info=sys.exc_info())
            print traceback.format_exc()
            if self.bubble_up_exception:
                raise exc
        else:
            self.call_hook('finished',video_url=self.url,
                                    video_location=save_at.abspath(),
                                    http_settings=self.http_settings,
                                    name_to_save_as=name_to_save_as)

            return True

    def get_video_info(self):

        go_to_video = self.go_to_video()
        stats = self.video_parser.get_video_stats(go_to_video)
        return stats

    def get_comments_from_page(self,page):

        session = self.http_settings.session
        proxy = self.http_settings.proxy
        url = 'http://www.youporn.com/ajax/'\
                'video/comments/{video_id}/top_comments/'\
                '?page={page}'.format(video_id=self.video_id,page=page)
        get_comments = session.get(url,proxies=proxy)

        #parse html and get all comments, returns YouPornComment objects
        comments,current_page,total_pages = self.video_parser.get_all_comments(html=get_comments.content)

        return(comments,current_page,total_pages)

    def get_comments(self,start_page=1,end_page=0):

        comments = []
        if start_page == 1 and end_page == 0:
            more_pages = True

            while more_pages:
                comments_from_page,current_page,total_pages = self.get_comments_from_page(page=start_page)
                comments.extend(comments_from_page)

                if current_page == total_pages:
                    more_pages = False

                start_page += 1

        else:
            for page_num in range(end_page):
                comments_from_page,current_page,total_pages = self.get_comments_from_page(page=page_num)
                comments.extend(comments_from_page)

        return comments

class YouPornVideoUploadRequest(VideoUploadRequest):
    DEFAULT_PASSWORD = "makemoneybitch"

    def __init__(self,video_file,title,tags,category,description,**kwargs):
        self.is_private = kwargs.get('is_private',False)
        if self.is_private:
            self.password = kwargs.get('password',self.DEFAULT_PASSWORD)
        else:
            self.password = ""

        self.thumbnail_id = kwargs.get('thumbnail_id',1)

        self.allow_comments = kwargs.get('allow_comments',True)
        self.porn_stars = kwargs.get('porn_stars',[])

        requirements = [(category,YouPornCategory,InvalidCategory),
                        (tags,YouPornTag,InvalidTag),
                        (title,YouPornTitle,InvalidTitle),
                        (description,YouPornDescription,InvalidDescription)]


        self._verify_upload_requirements(requirements)

        super(YouPornVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        category=category,
                                                        description=description,
                                                        **kwargs)

    def __repr__(self):

        return "<YouPorn UploadRequest title:{title} tags:{tags} category:{category}" \
            " description:{description}>".format(title=self.title.name,
                                                tags=",".join([t.name for t in self.tags]),
                                                category=self.category.name,
                                                description=self.description.name[:25])

    def create_video_settings(self):
        return {"title":str(self.title),
                "description":str(self.description),
                "tags":",".join([t.name for t in self.tags]),
                "porn_stars":",".join([t.name for p in self.porn_stars]),
                "is_private":"1" if self.is_private else "0",
                "password":self.password,
                "allow_comments":"0" if self.allow_comments else "1",
                "category_id":str(self.category.category_id),
                "orientation":"straight"}

class YouPornVideoUploaded(VideoUploaded):
    pass

if __name__ == '__main__':

    def downloading(**kwargs):
        print kwargs

    youporn_video = YouPornVideo(url='http://www.youporn.com/watch/4543/sexy-black-slut-squirting/?from=search_full&pos=11',
                                iter_size=1048576,
                                hooks={'downloading':downloading})
    #youporn_video.get_video_info()
    #info = youporn_video.get_video_info()
    #print info
    #youporn_video._verify_download_dir('shower.mp4')
    print youporn_video._hooks
    youporn_video.download(name_to_save_as='/root/Dropbox/interracial_pov.mp4')

    #print youporn_video.get_comments()


