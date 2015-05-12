#!/usr/bin/python
# -*- coding: utf-8 -*-
from bringyourownproxies.video import Category,Description,Title

class XhamsterTitle(Title):
    SITE = 'Xhamster'
    SITE_URL = 'www.youporn.com'

class XhamsterDescription(Description):
    SITE = 'Xhamster'
    SITE_URL = 'www.youporn.com'

class XhamsterCategory(Category):
    SITE = 'Xhamster'
    SITE_URL = 'www.drtuber.com'

    def __init__(self,name,**kwargs):

        self.category_id = kwargs.get('category_id',None)
        if self.category_id is None:
            get_category_id = self._find_category_id(category=name)

            if get_category_id is None:
                raise InvalidCategory('Invalid Category Name:{name}, it does not match a category id'.format(name=name))

            self.category_id = get_category_id

        super(XhamsterCategory,self).__init__(name=name,**kwargs)

class XhamsterCategoryStraight(XhamsterCategory):
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

class XhamsterCategoryGay(XhamsterCategory):
    CATEGORIES = {
		"amateur": "150",
		"asian": "151",
		"bareback": "152",
		"bdsm": "153",
		"beach": "154",
		"bears": "155",
		"big cocks": "156",
		"black gays": "106",
		"blowjobs": "157",
		"bukkake": "158",
		"crossdressers": "159",
		"cum tributes": "160",
		"daddies": "161",
		"emo boys": "162",
		"fat gays": "163",
		"fisting": "164",
		"gangbang": "165",
		"gaping": "166",
		"gays": "115",
		"glory holes": "167",
		"group sex": "168",
		"handjobs": "169",
		"hunks": "170",
		"interracial": "171",
		"latin": "172",
		"locker rooms": "173",
		"massage": "174",
		"masturbation": "175",
		"men": "80",
		"military": "177",
		"muscle": "178",
		"old+young": "179",
		"outdoor": "180",
		"sex toys": "181",
		"small cocks": "182",
		"spanking": "183",
		"striptease": "184",
		"twinks": "131",
		"vintage": "185",
		"voyeur": "186",
		"webcams": "187",
		"wrestling": "188"}
    def _find_category_id(self,category):

        if category.lower() in self.CATEGORIES:
            return self.CATEGORIES[category.lower()]

class XhamsterCategoryTranssexual(XhamsterCategory):
    CATEGORIES =  {
		"amateur": "189",
		"bareback": "190",
		"bdsm": "191",
		"big asses": "192",
		"big cocks": "193",
		"big tits": "194",
		"black": "217",
		"blowjobs": "195",
		"creampie": "196",
		"gangbang": "197",
		"guy fucks shemale": "198",
		"interracial": "199",
		"ladyboys": "141",
		"latex": "200",
		"latin": "201",
		"lingerie": "202",
		"masturbation": "203",
		"outdoor": "204",
		"pov": "205",
		"sex toys": "206",
		"shemale fucks girl": "207",
		"shemale fucks guy": "218",
		"shemale fucks shemale": "208",
		"shemales": "82",
		"small tits shemales": "209",
		"solo": "210",
		"stockings": "211",
		"teens": "212",
		"vintage": "214",
		"webcams": "216"}

    def _find_category_id(self,category):

        if category.lower() in self.CATEGORIES:
            return self.CATEGORIES[category.lower()]


