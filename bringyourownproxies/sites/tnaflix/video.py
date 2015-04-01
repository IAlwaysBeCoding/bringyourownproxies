#!/usr/bin/python
# -*- coding: utf-8 -*-
import uuid
import io
import re
import sys
import traceback

import path

from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.video import (OnlineVideo,VideoParser,VideoUploadRequest,
                                        VideoUploaded,Tag,Category,Description,Title)
from bringyourownproxies.errors import (InvalidVideoUrl,InvalidVideoParser,InvalidTag,InvalidCategory)
from bringyourownproxies.utils import show_printable_chars

from bringyourownproxies.sites.tnaflix.errors import InvalidTnaflixStar
from bringyourownproxies.sites.tnaflix.comment import TnaflixComment


class TnaflixCategory(Category):
    SITE = 'Tnaflix'
    SITE_URL = 'www.tnaflix.com'

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

            
        super(TnaflixCategory,self).__init__(name=name,**kwargs)
    
    def _find_category_id(self,category):

        categories= {'amateur':'1',
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
        
        if category.lower() in categories:
            return categories[category.lower()]

class TnaflixVideoUploadRequest(VideoUploadRequest):
    DEFAULT_PASSWORD = "makemoneybitch"
    
    def __init__(self,video_file,title,tags,category,description,**kwargs):
        self.is_private = kwargs.get('is_private',False)
        if self.is_private:
            self.password = kwargs.get('password',self.DEFAULT_PASSWORD)
        else:
            self.password = ""
            
        self.allow_comments = kwargs.get('allow_comments',True)
        self.porn_stars = kwargs.get('porn_stars',[])
        
        if type(self.porn_stars) == list or type(self.porn_stars) == tuple:
            for p in self.porn_stars:
                if type(p) != TnaflixStar:
                    raise InvalidTnaflixStar('Invalid TnaflixStar, it needs to be a TnaflixStar')
        else:
            if type(self.porn_stars) != TnaflixStar:
                raise InvalidTnaflixStar('Invalid TnaflixStar, it needs to be a TnaflixStar')
        
        if type(category) != TnaflixCategory:
            raise InvalidCategory('Invalid category, it needs to be a TnaflixCategory')

        
        if type(tags) == list or type(tags) == tuple:
            for t in tags:
                if type(t) != TnaflixTag:
                    raise InvalidTag('Invalid tag, it needs to be a TnaflixTag')
        else:
            if type(tags) != TnaflixTag:
                raise InvalidTag('Invalid tag, it needs to be a TnaflixTag')
        
        if type(category) != TnaflixCategory:
            raise InvalidCategory('Invalid category, it needs to be a TnaflixCategory')


        super(TnaflixVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        category=category,
                                                        description=description,
                                                        **kwargs)
        
    def __repr__(self):

        return "<Tnaflix UploadRequest title:{title} tags:{tags} category:{category}" \
            " description:{description}>".format(title=self.title.name,
                                                tags=",".join([t.name for t in self.tags]),
                                                category=self.category.name,
                                                description=self.description.name[:25])

    def create_video_settings(self):
        return {"title":str(self.title),
                "description":str(self.description),
                "tags":",".join([t.name for t in self.tags]),
                "porn_stars":",".join([t.name for p in self.porn_stars]),
                "is_private":"1" if self.is_private else "0",
                "password":self.password,
                "allow_comments":"0" if self.allow_comments else "1",
                "category_id":str(self.category.category_id),
                "orientation":"straight"}

class TnaflixVideoUploaded(VideoUploaded):
    pass

if __name__ == '__main__':

    def downloading(**kwargs):
        print kwargs
        
    tnaflix_video = TnaflixVideo(url='http://www.tnaflix.com/watch/10979257/exxxtrasmall-tiny-teen-sydney-cole-gets-drilled-by-a-huge-cock',
                                iter_size=1048576,
                                hooks={'downloading':downloading})
    #tnaflix_video.get_video_info()
    #info = tnaflix_video.get_video_info()
    #print info
    #tnaflix_video._verify_download_dir('shower.mp4')
    print tnaflix_video._hooks
    tnaflix_video.download(name_to_save_as='/home/testfiles/petite_drilled.mp4')

    #print tnaflix_video.get_comments()
    
    