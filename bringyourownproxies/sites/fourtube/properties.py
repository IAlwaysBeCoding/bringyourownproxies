# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.video import Tag,Category,Title

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

class _4tubeTitle(Title):
    SITE = '_4tube'
    SITE_URL = 'www.4tuber.com'

