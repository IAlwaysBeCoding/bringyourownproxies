#!/usr/bin/python
# -*- coding: utf-8 -*-
from bringyourownproxies.video import (VideoUploadRequest,VideoUploaded,Tag,Category,Title)
from bringyourownproxies.errors import (InvalidTag,InvalidCategory,InvalidTitle)


__all__ = ['FuxTitle','FuxTag','FuxCategory',
            'FuxVideoUploadRequest','FuxVideoUploaded']

class FuxTitle(Title):
    SITE = 'Fux'
    SITE_URL = 'www.fux.com'

class FuxTag(Tag):
    SITE = 'Fux'
    SITE_URL = 'www.fux.com'


class FuxCategory(Category):
    SITE = 'Fux'
    SITE_URL = 'www.fux.com'
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

        super(FuxCategory,self).__init__(name=name,**kwargs)


    def _find_category_id(self,category):

        if not category.lower() in self.CATEGORIES:
            raise InvalidCategory('Invalid category. Orientation can only be straight,gay or transsexual')
        else:
            return self.CATEGORIES[category.lower()]


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




