# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
from bringyourownproxies.video import VideoUploadRequest, VideoUploaded
from bringyourownproxies.errors import InvalidTag, InvalidTitle
from bringyourownproxies.sites.redtube.properties import RedTubeTag,RedTubeTitle

__all__ = ['RedTubeVideoUploadRequest', 'RedTubeVideoUploaded']

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
