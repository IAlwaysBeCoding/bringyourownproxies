# -*- coding: utf-8 -*-
#!/usr/bin/python
from bringyourownproxies.utils import show_printable_chars
from bringyourownproxies.video import Tag,Category,Description,Title
from bringyourownproxies.profile import Profile,BasicProfile,LocationProfile
from bringyourownproxies.author import OnlineAuthor
from bringyourownproxies.comment import OnlineComment

__all__ = ['YouPornTag','YouPornCategory','YouPornDescription',
           'YouPornTitle','YouPornProfile','YouPornAuthor',
           'YouPornComment']
class YouPornTag(Tag):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,name,**kwargs):
        self.href = kwargs.pop('href') if kwargs.get('href',False) else None

        super(YouPornTag,self).__init__(name=name,**kwargs)

class YouPornCategory(Category):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    CATEGORIES = {'amateur':'1',
                'hairy': '46',
                'brunette': '52',
                'squirting': '39',
                'german': '58',
                'bisexual': '5',
                'handjob': '22',
                'milf': '29',
                'fantasy': '42',
                'pantyhose': '57',
                'fingering': '62',
                'asian': '3',
                'latina': '49',
                'blonde': '51',
                'hentai': '23',
                'rimming': '43',
                'ebony': '8',
                'solo male': '60',
                'interview': '41',
                'gonzo': '50',
                'vintage': '33',
                'threesome': '38',
                'shaved': '54',
                'lesbian': '26',
                'pov': '36',
                'big butt': '6',
                'voyeur': '34',
                'bbw': '4',
                'fetish': '18',
                'shemale': '31',
                'panties': '56',
                'compilation': '11',
                'european': '48',
                'solo girl': '27',
                'cunnilingus': '15',
                'gay': '20',
                'funny': '19',
                'female friendly': '67',
                'big tits': '7',
                'redhead': '53',
                'blowjob': '9',
                'creampie': '13',
                'facial': '17',
                'kissing': '40',
                'webcam': '35',
                'anal': '2',
                'dp': '16',
                'couples': '12',
                'instructional': '24',
                'romantic': '61',
                'straight sex': '47',
                'dildos/toys': '44',
                'teen': '32',
                'public': '30',
                'cumshots': '37',
                'interracial': '25',
                'orgy': '21',
                'mature': '28',
                'college': '10',
                'swallow': '59',
                'massage': '64',
                'masturbation': '55'}

    def __init__(self,name,**kwargs):

        self.href = kwargs.pop('href') if kwargs.get('href',False) else None
        self.category_id = kwargs.get('category_id',None)
        if self.category_id is None:
            get_category_id = self._find_category_id(category=name)

            if get_category_id is None and self.href is not None:
                find_category_id = re.match('/(.*?)/(.*?)/(.*?)/',self.href,re.I|re.M)
                if find_category_id:
                    self.category_id = find_category_id.group(2)
                else:
                    raise InvalidCategory('Invalid Category Name, it does not match a category id')

            elif get_category_id is not None:
                self.category_id = get_category_id
            else:

                raise InvalidCategory('Invalid Category Name, it does not match a category id')


        super(YouPornCategory,self).__init__(name=name,**kwargs)

    def _find_category_id(self,category):

        if category.lower() in self.CATEGORIES:
            return self.CATEGORIES[category.lower()]

class YouPornDescription(Description):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

class YouPornTitle(Title):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

class YouPornProfile(Profile,BasicProfile,LocationProfile):
    def __init__(self,**kwargs):
        super(YouPornProfile,self).__init__(**kwargs)

class YouPornAuthor(OnlineAuthor):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,name,**kwargs):
        super(YouPornAuthor,self).__init__(name=name,**kwargs)

class YouPornComment(OnlineComment):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,author,text,comment_id,thumbs_up,thumbs_down,posted_date,**kwargs):

        self.comment_id = comment_id
        self.thumbs_up = thumbs_up
        self.thumbs_down = thumbs_down
        self.posted_date = posted_date
        super(YouPornComment,self).__init__(author=author,text=text,**kwargs)

    def __repr__(self):
        return "<{site}'s Comment(author:{a} id:{i} text:{t}...)>".format(site=self.SITE,
                                                                        a=show_printable_chars(self.author),
                                                                        i=self.comment_id,
                                                                        t=show_printable_chars(self.text)[:35])

    @classmethod
    def post_comment(cls,account,http_settings):
        pass

