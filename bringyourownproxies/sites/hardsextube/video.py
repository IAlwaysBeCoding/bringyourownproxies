# -*- coding: utf-8 -*-
#!/usr/bin/python
from bringyourownproxies.video import VideoUploadRequest,VideoUploaded
from bringyourownproxies.errors import (
    InvalidTag,
    InvalidCategory,
    InvalidDescription,
    InvalidTitle)

from bringyourownproxies.sites.hardsextube.properties import (HardSexTubeTitle,HardSexTubeDescription,
                                                              HardSexTubeTag,HardSexTubeCategoryStraight,
                                                              HardSexTubeCategoryGay,HardSexTubeCategoryTranssexual)



__all__ = ['HardSexTubeVideoUploadRequest','HardSexTubeVideoUploaded']

class HardSexTubeVideoUploadRequest(VideoUploadRequest):

    def __init__(
            self,
            video_file,
            title,
            tags,
            category,
            description,
            **kwargs):

        self.site_link = kwargs.get('site_link', None)
        self.site_name = kwargs.get('site_name', None)
        self.porn_star = kwargs.get('porn_star', None)
        self.thumbnail_id = kwargs.get('thumbnail_id', 1)

        requirements = [
            (category,
             (HardSexTubeCategoryStraight, HardSexTubeCategoryGay,
              HardSexTubeCategoryTranssexual), InvalidCategory),
            (tags, HardSexTubeTag, InvalidTag),
            (title, HardSexTubeTitle, InvalidTitle),
            (description, HardSexTubeDescription, InvalidDescription)]

        self._verify_upload_requirements(requirements)

        super(
            HardSexTubeVideoUploadRequest,
            self).__init__(
            video_file=video_file,
            title=title,
            tags=tags,
            category=category,
            description=description,
            **kwargs)

class HardSexTubeVideoUploaded(VideoUploaded):
    pass

    # print tnaflix_video.get_comments()
