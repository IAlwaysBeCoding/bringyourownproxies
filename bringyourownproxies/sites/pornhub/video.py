#!/usr/bin/python
# -*- coding: utf-8 -*-

from bringyourownproxies.video import VideoUploadRequest,VideoUploaded
from bringyourownproxies.errors import InvalidTag,InvalidCategory,InvalidTitle
from bringyourownproxies.sites.pornhub.properties import PornhubTitle,PornhubTag,PornhubCategory

__all__ = ['PornhubVideoUploadRequest','PornhubVideoUploaded']

class PornhubVideoUploadRequest(VideoUploadRequest):


    def __init__(self,video_file,title,tags,category,**kwargs):

        self.porn_stars = kwargs.get('porn_stars',None)
        self.is_private = kwargs.get('is_private',False)
        self.is_straight = kwargs.get('is_straight',True)
        self.is_homemade = kwargs.get('is_homemade',True)

        requirements = [(category,PornhubCategory,InvalidCategory),
                        (tags,PornhubTag,InvalidTag),
                        (title,PornhubTitle,InvalidTitle)]

        self._verify_upload_requirements(requirements)

        super(PornhubVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        category=category,
                                                        **kwargs)

class PornhubVideoUploaded(VideoUploaded):
    pass

