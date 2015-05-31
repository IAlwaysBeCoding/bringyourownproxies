# -*- coding: utf-8 -*-
#!/usr/bin/python
# -*- coding: utf-8 -*-

from bringyourownproxies.video import VideoUploadRequest,VideoUploaded
from bringyourownproxies.errors import InvalidTag,InvalidCategory,InvalidTitle
from bringyourownproxies.sites.porntube.properties import PornTubeTitle,PornTubeTag,PornTubeCategory

__all__ = ['PornTubeVideoUploadRequest','PornTubeVideoUploaded']

class PornTubeVideoUploadRequest(VideoUploadRequest):


    def __init__(self,video_file,title,tags,category,**kwargs):

        self.porn_stars = kwargs.get('porn_stars',None)

        self.autocorrect_tags = kwargs.get('autocorrect_tags',False)
        self.add_all_autocorrect_tags = kwargs.get('add_all_autocorrect_tags',False)
        self.drop_incorrect_tags = kwargs.get('drop_incorrect_tags',False)

        requirements = [(category,(PornTubeCategory),InvalidCategory),
                        (tags,PornTubeTag,InvalidTag),
                        (title,PornTubeTitle,InvalidTitle)]

        self._verify_upload_requirements(requirements)

        super(PornTubeVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        category=category,
                                                        **kwargs)

    def __repr__(self):

        return "<PornTube UploadRequest title:{title} tags:{tags} category:{category}" \
            " description:{description}>".format(title=self.title.name,
                                                tags=",".join([t.name for t in self.tags]),
                                                category=self.category.name,
                                                description=self.description.name[:25])

class PornTubeVideoUploaded(VideoUploaded):
    pass

