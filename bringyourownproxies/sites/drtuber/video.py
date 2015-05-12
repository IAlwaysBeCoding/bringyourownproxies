#!/usr/bin/python
# -*- coding: utf-8 -*-

from bringyourownproxies.video import VideoUploadRequest,VideoUploaded
from bringyourownproxies.errors import (InvalidVideoParser,InvalidTag,
                                        InvalidCategory,InvalidDescription,InvalidTitle)

from bringyourownproxies.sites.drtuber.properties import (DrTuberTitle,DrTuberTag,DrTuberDescription,
                                                          DrTuberCategory,DrTuberCategoryStraight,
                                                          DrTuberCategoryGay,DrTuberCategoryTranssexual)


__all__ = ['DrTuberVideoUploadRequest','DrTuberVideoUploaded']

class DrTuberVideoUploadRequest(VideoUploadRequest):


    def __init__(self,video_file,title,tags,category,description,**kwargs):

        self.site_link = kwargs.get('site_link',None)
        self.site_name = kwargs.get('site_name',None)
        self.porn_star = kwargs.get('porn_star',None)
        self.is_private = kwargs.get('is_private',False)
        self.thumbnail_id = kwargs.get('thumbnail_id',1)

        requirements = [(category,(DrTuberCategoryStraight,DrTuberCategoryGay,DrTuberCategoryTranssexual),InvalidCategory),
                        (tags,DrTuberTag,InvalidTag),
                        (title,DrTuberTitle,InvalidTitle),
                        (description,DrTuberDescription,InvalidDescription)]

        self._verify_upload_requirements(requirements)

        super(DrTuberVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        category=category,
                                                        description=description,
                                                        **kwargs)

class DrTuberVideoUploaded(VideoUploaded):
    pass


    #print tnaflix_video.get_comments()


