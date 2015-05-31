# -*- coding: utf-8 -*-
#!/usr/bin/python
from bringyourownproxies.video import Tag,Category,Title

__all__ = ['PornhubTitle','PornhubTag','PornhubCategory']

class PornhubTitle(Title):
    SITE = 'Pornhub'
    SITE_URL = 'www.pornhub.com'

class PornhubTag(Tag):
    SITE = 'Pornhub'
    SITE_URL = 'www.pornhub.com'

class PornhubCategory(Category):
    SITE = 'Pornhub'
    SITE_URL = 'www.pornhub.com'
    CATEGORIES = {
		"amateur": "3",
		"anal": "35",
		"arab": "98",
		"asian": "48",
		"babe": "5",
		"babysitter": "89",
		"bbw": "6",
		"behind the scenes": "141",
		"big ass": "4",
		"big dick": "58",
		"big tits": "8",
		"bisexual": "76",
		"blonde": "9",
		"blowjob": "56",
		"bondage": "10",
		"brazilian": "102",
		"british": "96",
		"brunette": "11",
		"bukkake": "14",
		"cartoon": "86",
		"casting": "90",
		"celebrity": "12",
		"college": "68",
		"compilation": "57",
		"creampie": "71",
		"cumshots": "16",
		"czech": "100",
		"double penetration": "72",
		"ebony": "17",
		"euro": "46",
		"feet": "93",
		"fetish": "52",
		"fisting": "19",
		"for women": "73",
		"french": "94",
		"funny": "32",
		"gangbang": "80",
		"german": "95",
		"handjob": "20",
		"hardcore": "21",
		"hentai": "36",
		"indian": "101",
		"interracial": "64",
		"italian": "97",
		"japanese": "39",
		"korean": "103",
		"latina": "26",
		"lesbian": "27",
		"massage": "45",
		"masturbation": "22",
		"mature": "28",
		"milf": "29",
		"music": "121",
		"old/young": "181",
		"orgy": "2",
		"parody": "201",
		"party": "53",
		"pissing": "211",
		"pov": "41",
		"public": "84",
		"pussy licking": "131",
		"reality": "85",
		"red head": "42",
		"rough sex": "67",
		"russian": "99",
		"school": "88",
		"shemale": "83",
		"small tits": "59",
		"smoking": "91",
		"solo male": "54",
		"squirt": "69",
		"striptease": "33",
		"teen": "37",
		"threesome": "65",
		"toys": "23",
		"uniforms": "81",
		"vintage": "77",
		"webcam": "61",
		"bareback": "40",
		"bear": "66",
		"black": "44",
		"daddy": "47",
		"group": "62",
		"hunks": "70",
		"latino": "50",
		"muscle": "51",
		"pornstar": "60",
		"straight guys": "82",
		"twink": "49"}

    def __init__(self,name,**kwargs):

        self.category_id = kwargs.get('category_id',None)
        if self.category_id is None:
            get_category_id = self._find_category_id(category=name)

            if get_category_id is None:
                raise InvalidCategory('Invalid Category Name:{name}, it does not match a category id'.format(name=name))

            self.category_id = get_category_id

        super(PornhubCategory,self).__init__(name=name,**kwargs)


    def _find_category_id(self,category):

        if not category.lower() in self.CATEGORIES:
            raise InvalidCategory('Invalid category. Orientation can only be straight,gay or transsexual')
        else:
            return self.CATEGORIES[category.lower()]

