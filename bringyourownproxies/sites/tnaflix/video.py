#!/usr/bin/python
# -*- coding: utf-8 -*-

from bringyourownproxies.video import VideoUploadRequest,VideoUploaded
from bringyourownproxies.errors import InvalidTag,InvalidCategory,InvalidDescription,InvalidTitle
from bringyourownproxies.sites.tnaflix.properties import (TnaflixTitle,TnaflixDescription,TnaflixTag,
                                                          TnaflixCategory)

__all__ = ['TnaflixVideoUploadRequest','TnaflixVideoUploaded']

class TnaflixVideoUploadRequest(VideoUploadRequest):


    def __init__(self,video_file,title,tags,category,description,**kwargs):

        requirements = [(category,TnaflixCategory,InvalidCategory),
                        (tags,TnaflixTag,InvalidTag),
                        (title,TnaflixTitle,InvalidTitle),
                        (description,TnaflixDescription,InvalidDescription)]

        self._verify_upload_requirements(requirements)

        super(TnaflixVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        category=category,
                                                        description=description,
                                                        **kwargs)

    def __repr__(self):

        return "<Tnaflix UploadRequest title:{title} tags:{tags} category:{category}" \
            " description:{description}>".format(title=self.title.name,
                                                tags=",".join([t.name for t in self.tags]),
                                                category=self.category.name,
                                                description=self.description.name[:25])

class TnaflixVideoUploaded(VideoUploaded):
    pass


    #print tnaflix_video.get_comments()


