#!/usr/bin/python
import uuid
import functools
import datetime

import path
from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.errors import (InvalidVideoCallable,InvalidVideoType,VideoFileDoesNotExist,
                                        InvalidTitle,InvalidTag,InvalidCategory,InvalidDescription)
from bringyourownproxies.httpclient import HttpSettings

class VideoObject(object):

    def __init__(self,name="",**kwargs):
        self.name = name
        
    def __repr__(self):
        return self.name
    
class Tag(VideoObject):
    pass

class Category(VideoObject):
    pass

class Description(VideoObject):
    pass

class Title(VideoObject):
    pass

class VideoParser(object):
    parser = HTMLParser()
    etree = etree
    tostring = tostring
    def get_video_stats(self,html):
        raise NotImplementedError('get_stats not implemented, this function returns the video stats like ratings, views, video length, author etc.')
        
    def get_download_url(self,html):
        raise NotImplementedError('get_download_url not implemented, this function should return the raw url video url to the current video')


class Video(object):
    
    def __init__(self,title=None,category=None,**kwargs):
        self.title = title
        self.category = category

    def __repr__(self):
        return "<Video title:{title} category:{category}>".format(title=self.title,category=self.category)
    
class OnlineVideo(Video):
    
    SITE = 'NOT SPECIFIED'
    SITE_URL = None

    def __init__(self,url,title,category,**kwargs):
        
        self.url = url
        self.http_settings = kwargs.pop('http_settings') if kwargs.get('http_settings',False) else HttpSettings()

        self.on_success_download = kwargs.pop('on_success_download') if kwargs.get('on_success_download',False) else functools.partial(lambda video_url,video_location : None) 
        self.on_failed_download = kwargs.pop('on_failed_download') if kwargs.get('on_failed_download',False) else functools.partial(lambda exception : None) 

        #setup callback functions to call whenever a successful download or failed download is done.
        #The callbacks need to be a functools.partial object
        if (type(self.on_success_download) != functools.partial ):
            raise InvalidVideoCallable('on_success_download needs to be a partial object type')
        if (type(self.on_failed_download) != functools.partial):
            raise InvalidVideoCallable('on_failed_download needs to be a partial object type')
        
        super(OnlineVideo,self).__init__(title=title,category=category,**kwargs)

    def download(self):
        raise NotImplementedError('Download method must be implemented by classes subclassing from OnlineVideo class')
    
    def go_to_video(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        #check that the video url belongs to a Youporn.com video, else raise an error.
        if self.SITE_URL not in self.url:
            raise InvalidVideoUrl('Invalid video url, video does not belong to YouPorn.com')
        
        video = session.get(self.url,proxies=proxy)
        return video.content
    

    def _verify_download_dir(self,name_to_save_as=None):
        if not name_to_save_as:
            name_to_save_as = str(uuid.uuid4())

        directory = path.Path(name_to_save_as).parent
        path_exists = path.Path(directory).exists()
        
        if directory == '':
            directory = path.Path(name_to_save_as).getcwd()

        if not path_exists:
            path.Path(directory).makedirs_p()

        return (directory,name_to_save_as)            

class VideoUploadRequest(object):

    def __init__(self,
                video_file,
                title=Title(),
                tags=(Tag(),),
                category=Category(),
                description=Description(),
                **kwargs):
        
        self.video_file = video_file
        self._verify_video_file()
        
        if not isinstance(title, Title):
            raise InvalidTitle('title is not a valid Title instance')
        if not isinstance(category, Category):
            raise InvalidCategory('category is not a valid Category instance')
        if not isinstance(description, Description):
            raise InvalidDescription('description is not a valid Description instance')
        
        if type(tags) == list or type(tags) == tuple:
            for t in tags:
                if not isinstance(t, Tag):
                    raise InvalidTag('t is not a valid Tag instance')
        else:
            if not isinstance(tags, Tag):
                raise InvalidTag('tags is not a valid Tag instance')

        self.title = title
        self.tags = tags
        self.category = category
        self.description = description
        self._success = None
        super(VideoUploadRequest,self).__init__(**kwargs)        

    def __repr__(self):

        return "<VideoUploadRequest title:{title} tags:{tags} category:{category}" \
                " description:{description}>".format(title=self.title,
                                                    tags=",".join(self.tags),
                                                    category=self.category,
                                                    description=self.description[:25])

    def _verify_video_file(self):
        video_path = path.Path(self.video_file)

        if not video_path.isfile():
            raise InvalidVideoType('video_file is not a valid path to a video file')
        if not video_path.exists():
            raise VideoFileDoesNotExist('video_file does not point to a valid file')
    
    def succeeded(self):
        self._success = True
    
    def failed(self):
        self._success = False
    
    def status(self):
        return self._success
    
    
class VideoUploaded(object):
    SITE = 'NOT SPECIFIED'
    SITE_URL = None
    
    def __init__(self,
                url,
                video_id=None,
                title=Title(),
                tags=(Tag(),),
                category=Category(),
                description=Description(),
                username=None,
                date_uploaded=datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                **kwargs):

        if not isinstance(title, Title):
            raise InvalidTitle('title is not a valid Title instance')
        if not isinstance(category, Category):
            raise InvalidCategory('category is not a valid Category instance')
        if not isinstance(description, Description):
            raise InvalidDescription('description is not a valid Description instance')
        
        if type(tags) == list or type(tags) == tuple:
            for t in tags:
                if not isinstance(t, Tag):
                    raise InvalidTag('t is not a valid Tag instance')
        else:
            if not isinstance(tags, Tag):
                raise InvalidTag('tags is not a valid Tag instance')
            

        self.url = url
        self.video_id = video_id
        self.title = title
        self.tags = tags
        self.category = category
        self.description = description
        self.username = username
        self.date_uploaded = date_uploaded
        
        super(VideoUploaded,self).__init__(**kwargs)
    
    def __repr__(self):
        return "<{sites}'s VideoUploaded Title:{title} Tags:{tags}" \
                " Category:{category} Uploaded Date:{date_uploaded}".format(sites=self.SITE,
                                                                    title=self.title,
                                                                    tags=",".join(self.tags),
                                                                    category=self.category,
                                                                    date_uploaded=self.date_uploaded)
        
        
    