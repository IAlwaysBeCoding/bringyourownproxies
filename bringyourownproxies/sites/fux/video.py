# -*- coding: utf-8 -*-
#!/usr/bin/python
from bringyourownproxies.video import VideoUploadRequest,VideoUploaded
from bringyourownproxies.errors import InvalidTag,InvalidCategory,InvalidTitle
from bringyourownproxies.sites.fux.properties import FuxTitle,FuxTag,FuxCategory

__all__ = ['FuxVideoUploadRequest','FuxVideoUploaded']

class FuxVideoUploadRequest(VideoUploadRequest):


    def __init__(self,video_file,title,tags,category,**kwargs):

        self.porn_stars = kwargs.get('porn_stars',None)

        self.autocorrect_tags = kwargs.get('autocorrect_tags',False)
        self.add_all_autocorrect_tags = kwargs.get('add_all_autocorrect_tags',False)
        self.drop_incorrect_tags = kwargs.get('drop_incorrect_tags',False)

        requirements = [(category,(FuxCategory),InvalidCategory),
                        (tags,FuxTag,InvalidTag),
                        (title,FuxTitle,InvalidTitle)]

        self._verify_upload_requirements(requirements)

        super(FuxVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        category=category,
                                                        **kwargs)

    def __repr__(self):

        return "<Fux UploadRequest title:{title} tags:{tags} category:{category}" \
            " description:{description}>".format(title=self.title.name,
                                                tags=",".join([t.name for t in self.tags]),
                                                category=self.category.name,
                                                description=self.description.name[:25])

class FuxVideoUploaded(VideoUploaded):
    pass




