
from bringyourownproxies.video import Tag,Category,Title

__all__ = ['FuxTag','FuxCategory','FuxTitle']

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

class FuxTitle(Title):
    SITE = 'Fux'
    SITE_URL = 'www.fux.com'

