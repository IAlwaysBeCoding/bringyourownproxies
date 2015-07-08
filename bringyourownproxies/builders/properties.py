from bringyourownproxies.video import Tag,Category,Description,Title

from bringyourownproxies.sites import YouPornTag,YouPornCategory,YouPornDescription,YouPornTitle

from bringyourownproxies.sites import (DrTuberTitle,DrTuberTag,DrTuberDescription,
                                       DrTuberCategoryStraight,DrTuberCategoryGay,
                                       DrTuberCategoryTranssexual)

from bringyourownproxies.sites import (HardSexTubeTitle,HardSexTubeDescription,
                                      HardSexTubeTag,HardSexTubeCategoryStraight,
                                      HardSexTubeCategoryGay,HardSexTubeCategoryTranssexual)

from bringyourownproxies.sites import PornhubTitle,PornhubTag,PornhubCategory

from bringyourownproxies.sites import RedTubeTitle,RedTubeTag

from bringyourownproxies.sites import SexTag,SexTitle

from bringyourownproxies.sites import TnaflixTitle,TnaflixDescription,TnaflixTag,TnaflixCategory

from bringyourownproxies.sites import (XhamsterCategoryStraight,XhamsterCategoryGay,
                                        XhamsterCategoryTranssexual,XhamsterTitle,
                                        XhamsterDescription)

from bringyourownproxies.sites import XvideosTag,XvideosDescription,XvideosTitle

from bringyourownproxies.builders.base import BaseBuilder
from bringyourownproxies.builders.errors import (CategoryBuilderException,TagBuilderException,
                                                 TitleBuilderException,DescriptionBuilderException)


__all__ = ['CategoryBuilder','TitleBuilder','DescriptionBuilder','TagBuilder']

class CategoryBuilder(BaseBuilder):

    klazz_category_exception = CategoryBuilderException
    klazz_category = Category

    SITES = {'youporn':YouPornCategory,
             'drtuber':{'straight':DrTuberCategoryStraight,
                        'gay':DrTuberCategoryGay,
                        'transsexual':DrTuberCategoryTranssexual
                        },
             'hardsextube':{'straight':HardSexTubeCategoryStraight,
                            'gay':HardSexTubeCategoryGay,
                            'transsexual':HardSexTubeCategoryTranssexual
                            },
             'pornhub':PornhubCategory,
             'redtube':Category,
             'sex':Category,
             'tnaflix':TnaflixCategory,
             'xhamster':{'straight':XhamsterCategoryStraight,
                         'gay':XhamsterCategoryGay,
                         'transsexual':XhamsterCategoryTranssexual
                        },
             'xvideos':Category
            }

    def __init__(self,site):
        super(CategoryBuilder,self).__init__(site)
        self.klazz_category = self.SITES[site]

    def __call__(self,name,**kwargs):
        return self.create_category(name,**kwargs)

    def get_supported_categories(self,category_type=None):
        if isinstance(self.klazz_category,dict) and category_type is None:
            raise CategoryBuilderException('Category type needs to be passed.It needs '\
                                           'to be straight,gay, or transsexual ')

        category_class = self.get_category_class(category=category_type)

        return [key for key in category_class.CATEGORIES.keys()]

    def get_category_class(self,category):
        if not isinstance(self.klazz_category,dict):
            raise CategoryBuilderException('There is no {c} class'.format(c=category))

        category_type = self.klazz_category.get(category,None)

        if not category_type:
            raise CategoryBuilderException('Missing category:{c}'.format(c=category))

        return category_type

    def create_category(self,name,**kwargs):
        if isinstance(self.klazz_category,dict):
            category_type = kwargs.get('category_type',None)

            if not category_type:
                raise CategoryBuilderException('Missing category_type')

            klazz = self.get_category_class(category_type)
            return klazz(name)

        print 'passing to create category:{s}'.format(s=name)
        return self.klazz_category(name)

class TagBuilder(BaseBuilder):

    klazz_tag_exception = TagBuilderException
    klazz_tag = Tag

    SITES = {'youporn':YouPornTag,
             'drtuber':DrTuberTag,
             'hardsextube':HardSexTubeTag,
             'pornhub':PornhubTag,
             'redtube':RedTubeTag,
             'sex':SexTag,
             'tnaflix':TnaflixTag,
             'xhamster':Tag,
             'xvideos':XvideosTag
             }

    def __init__(self,site):
        super(TagBuilder,self).__init__(site)
        self.klazz_tag = self.SITES[site]

    def __call__(self,name,**kwargs):
        return self.create_tag(name,**kwargs)

    def create_tag(self,name,**kwargs):
        return self.klazz_tag(name=name,**kwargs) if self.klazz_tag else None

class DescriptionBuilder(BaseBuilder):

    klazz_description_exception = DescriptionBuilderException
    klazz_description = Description

    SITES = {'youporn':YouPornDescription,
             'drtuber':DrTuberDescription,
             'hardsextube':HardSexTubeDescription,
             'pornhub':Description,
             'redtube':Description,
             'sex':Description,
             'tnaflix':TnaflixDescription,
             'xhamster':XhamsterDescription,
             'xvideos':XvideosDescription
             }

    def __init__(self,site):
        super(DescriptionBuilder,self).__init__(site)
        self.klazz_description = self.SITES[site]

    def __call__(self,name,**kwargs):
        return self.create_description(name=name,**kwargs)

    def create_description(self,name,**kwargs):
        return self.klazz_description(name=name,**kwargs) if self.klazz_description else None

class TitleBuilder(BaseBuilder):

    klazz_title_exception = TitleBuilderException
    klazz_title = Title

    SITES = {'youporn':YouPornTitle,
             'drtuber':DrTuberTitle,
             'hardsextube':HardSexTubeTitle,
             'pornhub':PornhubTitle,
             'redtube':RedTubeTitle,
             'sex':SexTitle,
             'tnaflix':TnaflixTitle,
             'xhamster':XhamsterTitle,
             'xvideos':XvideosTitle
             }

    def __init__(self,site):
        super(TitleBuilder,self).__init__(site)
        self.klazz_title = self.SITES[site]

    def __call__(self,name,**kwargs):
        return self.create_title(name=name,**kwargs)

    def create_title(self,name,**kwargs):
        return self.klazz_title(name=name,**kwargs) if self.klazz_title else None


