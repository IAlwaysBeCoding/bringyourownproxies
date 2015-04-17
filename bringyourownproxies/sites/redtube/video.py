#!/usr/bin/python
# -*- coding: utf-8 -*-
from bringyourownproxies.video import VideoUploadRequest, VideoUploaded, Tag, Title
from bringyourownproxies.errors import InvalidTag, InvalidTitle


__all__ = ['RedTubeTitle', 'RedTubeTag',
           'RedTubeVideoUploadRequest', 'RedTubeVideoUploaded']


class RedTubeTitle(Title):
    SITE = 'RedTube'
    SITE_URL = 'www.pornhub.com'


class RedTubeTag(Tag):
    SITE = 'RedTube'
    SITE_URL = 'www.pornhub.com'


class RedTubeVideoUploadRequest(VideoUploadRequest):

    def __init__(self, video_file, title, tags, **kwargs):

        self.porn_stars = kwargs.get('porn_stars', None)
        self.is_private = kwargs.get('is_private',None)

        requirements = [(tags, RedTubeTag, InvalidTag),
                        (title, RedTubeTitle, InvalidTitle)]

        self._verify_upload_requirements(requirements)

        super(RedTubeVideoUploadRequest, self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        **kwargs)


class RedTubeVideoUploaded(VideoUploaded):
    pass
