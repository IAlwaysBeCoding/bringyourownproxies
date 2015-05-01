#!/usr/bin/python
# -*- coding: utf-8 -*-
from bringyourownproxies.video import (VideoUploadRequest,VideoUploaded,Tag,Category,Title)
from bringyourownproxies.errors import (InvalidTag,InvalidCategory,InvalidTitle)



__all__ = ['_4tubeTitle','_4tubeTag','_4tubeCategory',
            '_4tubeVideoUploadRequest','_4tubeVideoUploaded']

class _4tubeTitle(Title):
    SITE = '_4tube'
    SITE_URL = 'www.4tuber.com'

class _4tubeTag(Tag):
    SITE = '_4tube'
    SITE_URL = 'www.4tuber.com'


class _4tubeCategory(Category):
    SITE = '_4tube'
    SITE_URL = 'www.4tuber.com'
    CATEGORIES = {'straight':1,
                'gay':2,
                'shemale':3}
    def __init__(self,name,**kwargs):

        self.category_id = kwargs.get('category_id',None)
        if self.category_id is None:
            get_category_id = self._find_category_id(category=name)

            if get_category_id is None:
                raise InvalidCategory('Invalid Category Name:{name}, it does not match a category id'.format(name=name))

            self.category_id = get_category_id

        super(_4tubeCategory,self).__init__(name=name,**kwargs)


    def _find_category_id(self,category):

        if not category.lower() in self.CATEGORIES:
            raise InvalidCategory('Invalid category. Orientation can only be straight,gay or transsexual')
        else:
            return self.CATEGORIES[category.lower()]


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

