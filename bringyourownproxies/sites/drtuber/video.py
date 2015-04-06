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
from bringyourownproxies.errors import (InvalidVideoUrl,InvalidVideoParser,InvalidTag,
                                        InvalidCategory,InvalidDescription,InvalidTitle)
from bringyourownproxies.utils import show_printable_chars


__all__ = ['DrTuberTitle','DrTuberDescription','DrTuberTag',
            'DrTuberCategory','DrTuberCategoryStraight','DrTuberCategoryGay',
            'DrTuberCategoryTranssexual','DrTuberVideoUploadRequest','DrTuberVideoUploaded']
	            
class DrTuberTitle(Title):
    SITE = 'DrTuber'
    SITE_URL = 'www.tnaflix.com'

class DrTuberDescription(Description):
    SITE = 'DrTuber'
    SITE_URL = 'www.tnaflix.com'

class DrTuberTag(Tag):
    SITE = 'DrTuber'
    SITE_URL = 'www.tnaflix.com'


class DrTuberCategory(Category):
    SITE = 'DrTuber'
    SITE_URL = 'www.tnaflix.com'

    def __init__(self,name,**kwargs):

        self.category_id = kwargs.get('category_id',None)
        if self.category_id is None:
            get_category_id = self._find_category_id(category=name)

            if get_category_id is None:
                raise InvalidCategory('Invalid Category Name:{name}, it does not match a category id'.format(name=name))

            self.category_id = get_category_id
            
        super(DrTuberCategory,self).__init__(name=name,**kwargs)
    

class DrTuberCategoryStraight(DrTuberCategory):
    CATEGORIES = {
		"3d": "178",
		"amateur": "1",
		"anal": "2",
		"asian": "3",
		"ass": "4",
		"asslick": "191",
		"babe": "5",
		"bbw": "7",
		"bdsm": "8",
		"beach": "9",
		"big boobs": "10",
		"big cocks": "169",
		"bisexual": "11",
		"black and ebony": "12",
		"blonde": "13",
		"blowjob": "14",
		"brazilian": "15",
		"british": "16",
		"brunette": "17",
		"bukkake": "18",
		"casting": "190",
		"celebrity": "20",
		"cfnm": "28",
		"chinese": "21",
		"close-up": "22",
		"college": "27",
		"creampie": "23",
		"cuckold": "24",
		"cumshot": "25",
		"czech": "26",
		"doggystyle": "189",
		"double penetration": "30",
		"erotic": "31",
		"european": "32",
		"facial": "181",
		"fat": "35",
		"femdom": "36",
		"fetish": "37",
		"fingering": "180",
		"first time": "176",
		"fisting": "38",
		"foot fetish": "33",
		"french": "34",
		"funny": "39",
		"gangbang": "40",
		"gaping": "41",
		"german": "42",
		"glory hole": "177",
		"granny": "44",
		"group sex": "43",
		"hairy": "45",
		"handjob": "47",
		"hardcore": "48",
		"hentai": "49",
		"hidden cams": "50",
		"indian": "51",
		"interracial": "52",
		"italian": "53",
		"japanese": "54",
		"korean": "55",
		"latex": "56",
		"latin": "57",
		"lesbian": "58",
		"lick": "179",
		"lingerie": "59",
		"massage": "60",
		"masturbation": "61",
		"mature": "62",
		"milf": "63",
		"nipples": "64",
		"nylon": "65",
		"old+young": "66",
		"outdoor": "69",
		"panties": "71",
		"pornstar": "67",
		"pov": "68",
		"public": "70",
		"reality": "72",
		"redhead": "73",
		"russian": "74",
		"shower": "75",
		"small cocks": "182",
		"small tits": "183",
		"softcore": "77",
		"solo": "76",
		"spanking": "78",
		"squirting": "79",
		"stockings": "80",
		"strapon": "81",
		"striptease": "82",
		"swingers": "84",
		"teen": "85",
		"thai": "88",
		"threesome": "86",
		"titjob": "188",
		"toys": "87",
		"uniform": "91",
		"upskirt": "90",
		"vintage": "92",
		"voyeur": "93",
		"webcam": "94"}
    
    def _find_category_id(self,category):

        if category.lower() in self.CATEGORIES:
            return self.CATEGORIES[category.lower()]

class DrTuberCategoryGay(DrTuberCategory):
    CATEGORIES = {
                "amateur": "6",
                "anal & ass": "4",
                "arabian": "65",
                "asians": "17",
                "babes": "26",
                "bbw": "32",
                "bdsm": "66",
                "bizarre": "47",
                "blonde": "50",
                "blowjobs & oral sex": "7",
                "brunette": "51",
                "bukkake": "67",
                "cartoon": "28",
                "celebrity": "63",
                "classic": "31",
                "creampie": "15",
                "cumshots": "3",
                "czech": "68",
                "double penetration": "21",
                "ebony": "16",
                "euro porn": "56",
                "facial cum shots": "54",
                "fat girls": "49",
                "fetish sex": "25",
                "fisting": "14",
                "foot fetish": "48",
                "french": "69",
                "gang bang": "20",
                "gay / bi-male": "30",
                "german porn": "61",
                "granny": "41",
                "group sex": "10",
                "hairy": "39",
                "handjobs": "70",
                "hardcore porn": "1",
                "hd videos": "64",
                "hentai": "46",
                "homemade": "35",
                "huge cocks": "27",
                "huge tits": "13",
                "indian": "45",
                "interracial": "12",
                "japanese": "62",
                "latinas": "18",
                "lesbian": "11",
                "massage": "71",
                "masturbation": "8",
                "mature": "9",
                "milf": "43",
                "oral": "72",
                "petite": "24",
                "piss": "34",
                "compilations": "79",
                "pov": "29",
                "pregnant": "36",
                "public": "40",
                "reality porn": "53",
                "redhead": "52",
                "russian": "73",
                "sex toys": "44",
                "shemale/trans": "23",
                "softcore": "22",
                "solo": "74",
                "spanking": "42",
                "squirting": "5",
                "storyline": "33",
                "strapon": "75",
                "teens 18+": "2",
                "thai": "76",
                "threesome": "80",
                "vintage": "77",
                "webcam": "78"}
    
    def _find_category_id(self,category):
           
        if category.lower() in self.CATEGORIES:
            return self.CATEGORIES[category.lower()]

class DrTuberCategoryTranssexual(DrTuberCategory):
       
    CATEGORIES = {
		"amateur": "138",
		"asian": "173",
		"asslick": "195",
		"bareback": "139",
		"bdsm": "140",
		"big asses": "141",
		"big cocks": "142",
		"big tits": "143",
		"black and ebony": "144",
		"blowjob": "145",
		"creampie": "146",
		"cumshot": "193",
		"european": "175",
		"gangbang": "147",
		"group sex": "174",
		"guy fucks shemale": "148",
		"handjob": "194",
		"interracial": "150",
		"ladyboys": "151",
		"latex": "152",
		"latin": "153",
		"lingerie": "154",
		"masturbation": "155",
		"outdoor": "156",
		"pov": "157",
		"shemale fucks girl": "159",
		"shemale fucks guy": "160",
		"shemale fucks shemale": "161",
		"shemales": "162",
		"small tits shemales": "163",
		"solo": "164",
		"stockings": "165",
		"teens": "166",
		"toys": "158",
		"webcam": "168"}
    
    def _find_category_id(self,category):

        if category.lower() in self.CATEGORIES:
            return self.CATEGORIES[category.lower()]

class DrTuberVideoUploadRequest(VideoUploadRequest):

    
    def __init__(self,video_file,title,tags,category,description,**kwargs):
        
        self.site_link = kwargs.get('site_link',None)
        self.site_name = kwargs.get('site_name',None)
        self.porn_star = kwargs.get('porn_star',None)
        self.is_private = kwargs.get('is_private',False)
        self.thumbnail_id = kwargs.get('thumbnail_id',1)
        
        requirements = [(category,(DrTuberCategoryStraight,DrTuberCategoryGay,DrTuberCategoryTranssexual),InvalidCategory),
                        (tags,DrTuberTag,InvalidTag),
                        (title,DrTuberTitle,InvalidTitle),
                        (description,DrTuberDescription,InvalidDescription)]
        
        self._verify_upload_requirements(requirements)
        
        super(DrTuberVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        category=category,
                                                        description=description,
                                                        **kwargs)
        
    def __repr__(self):

        return "<DrTuber UploadRequest title:{title} tags:{tags} category:{category}" \
            " description:{description}>".format(title=self.title.name,
                                                tags=",".join([t.name for t in self.tags]),
                                                category=self.category.name,
                                                description=self.description.name[:25])


class DrTuberVideoUploaded(VideoUploaded):
    pass


    #print tnaflix_video.get_comments()
    
    