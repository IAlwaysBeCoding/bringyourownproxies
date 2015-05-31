# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
from bringyourownproxies.video import (VideoUploadRequest,VideoUploaded,Tag,Category,Title)
from bringyourownproxies.errors import (InvalidTag,InvalidCategory,InvalidTitle)
from bringyourownproxies.sites.fourtube.properties import _4tubeTag,_4tubeCategory,_4tubeTitle


__all__ = ['_4tubeVideoUploadRequest','_4tubeVideoUploaded']

class _4tubeVideoUploadRequest(VideoUploadRequest):


    def __init__(self,video_file,title,tags,category,**kwargs):

        self.porn_stars = kwargs.get('porn_stars',None)

        self.autocorrect_tags = kwargs.get('autocorrect_tags',False)
        self.add_all_autocorrect_tags = kwargs.get('add_all_autocorrect_tags',False)
        self.drop_incorrect_tags = kwargs.get('drop_incorrect_tags',False)

        requirements = [(category,(_4tubeCategory),InvalidCategory),
                        (tags,_4tubeTag,InvalidTag),
                        (title,_4tubeTitle,InvalidTitle)]

        self._verify_upload_requirements(requirements)

        super(_4tubeVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        category=category,
                                                        **kwargs)

    def __repr__(self):

        return "<_4tube UploadRequest title:{title} tags:{tags} category:{category}" \
            " description:{description}>".format(title=self.title.name,
                                                tags=",".join([t.name for t in self.tags]),
                                                category=self.category.name,
                                                description=self.description.name[:25])

class _4tubeVideoUploaded(VideoUploaded):
    pass

