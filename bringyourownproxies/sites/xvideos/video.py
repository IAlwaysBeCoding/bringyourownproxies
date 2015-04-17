#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import traceback

import path

from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.video import VideoUploadRequest,VideoUploaded,Tag,Description,Title
from bringyourownproxies.errors import InvalidTag,InvalidDescription,InvalidTitle


__all__ = ['XvideosTitle','XvideosTag','XvideosDescription',
            'XvideosVideoUploadRequest','XvideosVideoUploaded']
                
class XvideosTitle(Title):
    SITE = 'Xvideos'
    SITE_URL = 'www.xvideos.com'

class XvideosTag(Tag):
    SITE = 'Xvideos'
    SITE_URL = 'www.xvideos.com'

class XvideosDescription(Description):
	
	SITE = 'Xvideos'
	SITE_URL = 'www.xvideos.com'

class XvideosVideoUploadRequest(VideoUploadRequest):

    def __init__(self,video_file,title,tags,description,**kwargs):
        
        self.is_private = kwargs.get('is_private',False)
        self.orientation = kwargs.get('orientation','straight')

        requirements = [(tags,XvideosTag,InvalidTag),
                        (description,XvideosDescription,InvalidDescription),
                        (title,XvideosTitle,InvalidTitle)]
        
        self._verify_upload_requirements(requirements)
        
        super(XvideosVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        **kwargs)
    def create_video_settings(self):
    	
    	return {'title':self.title.name,
    			'tags':[t.name for t in self.tags],
    			'is_private':'1' if self.is_private else '0',
    			'description':self.description.name}

class XvideosVideoUploaded(VideoUploaded):
    pass
