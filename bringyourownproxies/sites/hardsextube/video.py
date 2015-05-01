#!/usr/bin/python
# -*- coding: utf-8 -*-
from bringyourownproxies.video import (VideoUploadRequest, VideoUploaded, Tag,
                                       Category, Description, Title)
from bringyourownproxies.errors import (
    InvalidTag,
    InvalidCategory,
    InvalidDescription,
    InvalidTitle)


__all__ = [
    'HardSexTubeTitle',
    'HardSexTubeDescription',
    'HardSexTubeTag',
    'HardSexTubeCategory',
    'HardSexTubeCategoryStraight',
    'HardSexTubeCategoryGay',
    'HardSexTubeCategoryTranssexual',
    'HardSexTubeVideoUploadRequest',
    'HardSexTubeVideoUploaded']


class HardSexTubeTitle(Title):
    SITE = 'HardSexTube'
    SITE_URL = 'www.hardsextube.com'


class HardSexTubeDescription(Description):
    SITE = 'HardSexTube'
    SITE_URL = 'www.hardsextube.com'


class HardSexTubeTag(Tag):
    SITE = 'HardSexTube'
    SITE_URL = 'www.hardsextube.com'


class HardSexTubeCategory(Category):
    SITE = 'HardSexTube'
    SITE_URL = 'www.hardsextube.com'

    def __init__(self, name, **kwargs):

        self.category_id = kwargs.get('category_id', None)
        if self.category_id is None:
            get_category_id = self._find_category_id(category=name)

            if get_category_id is None:
                raise InvalidCategory(
                    'Invalid Category Name:{name}, it does not match a category id'.format(
                        name=name))

            self.category_id = get_category_id

        super(HardSexTubeCategory, self).__init__(name=name, **kwargs)


class HardSexTubeCategoryStraight(HardSexTubeCategory):
    CATEGORIES = {
        "hairy": "73",
        "group": "71",
        "homemade": "83",
        "doctor": "53",
        "vintage": "139",
        "deepthroat": "51",
        "swinger": "131",
        "teen": "135",
        "big cock": "21",
        "spanking": "127",
        "pov": "115",
        "hidden cam": "81",
        "black": "25",
        "latina": "229",
        "bdsm": "15",
        "brazilian": "31",
        "bbw": "13",
        "party": "111",
        "korean": "95",
        "public": "117",
        "ebony": "55",
        "rough": "119",
        "ass": "9",
        "babe": "11",
        "beauty": "17",
        "petite": "113",
        "compilation": "45",
        "wife": "143",
        "french": "61",
        "schoolgirl": "123",
        "arab": "5",
        "blowjob": "29",
        "creampie": "47",
        "granny": "69",
        "russian": "121",
        "hardcore": "77",
        "italian": "89",
        "emo": "57",
        "old and young": "185",
        "cumshot": "49",
        "shemale": "125",
        "gangbang": "63",
        "jav": "93",
        "teacher": "133",
        "celebrity": "41",
        "british": "33",
        "interracial": "87",
        "mature": "105",
        "casting": "39",
        "anal": "3",
        "femdom": "59",
        "massage": "101",
        "amateur": "1",
        "lesbian": "99",
        "busty": "37",
        "brunette": "35",
        "gay": "225",
        "webcam": "141",
        "threesome": "137",
        "german": "65",
        "bisexual": "23",
        "squirting": "129",
        "masturbation": "103",
        "japanese": "91",
        "handjob": "75",
        "milf": "107",
        "orgasm": "109",
        "indian": "85",
        "college": "43",
        "asian": "7",
        "girlfriend": "67",
        "blonde": "27",
        "hentai": "79",
        "pornstars": "231",
        "big boobs": "19"
    }

    def _find_category_id(self, category):

        if category.lower() in self.CATEGORIES:
            return self.CATEGORIES[category.lower()]


class HardSexTubeCategoryGay(HardSexTubeCategory):

    CATEGORIES = {
            "group": "71",
            "twink": "189",
            "big cock": "21",
            "black": "25",
            "bdsm": "15",
            "fisting": "165",
            "latin": "97",
            "amateur": "1",
            "bear": "151",
            "bareback": "149",
            "blowjob": "29",
            "old and young": "185",
            "webcam": "141",
            "gangbang": "63",
            "emo": "57",
            "interracial": "87",
            "hunk": "173",
            "muscle": "183",
            "massage": "101",
            "masturbation": "103",
            "handjob": "75",
            "daddy": "161",
            "asian": "7",
            "toys": "187"}

    def _find_category_id(self, category):
        if category.lower() in self.CATEGORIES:
            return self.CATEGORIES[category.lower()]


class HardSexTubeCategoryTranssexual(HardSexTubeCategory):

    CATEGORIES = {
        "teen": "135",
        "webcam": "141",
        "amateur": "1",
        "gangbang": "63",
        "pov": "115",
        "toys": "187",
        "big tits": "199",
        "bareback": "149",
        "blowjob": "29",
        "black": "25",
        "bdsm": "15",
        "small tits": "217",
        "fucks guy": "209",
        "creampie": "47",
        "fucks girl": "207",
        "masturbation": "103"
    }

    def _find_category_id(self, category):

        if category.lower() in self.CATEGORIES:
            return self.CATEGORIES[category.lower()]


class HardSexTubeVideoUploadRequest(VideoUploadRequest):

    def __init__(
            self,
            video_file,
            title,
            tags,
            category,
            description,
            **kwargs):

        self.site_link = kwargs.get('site_link', None)
        self.site_name = kwargs.get('site_name', None)
        self.porn_star = kwargs.get('porn_star', None)
        self.thumbnail_id = kwargs.get('thumbnail_id', 1)

        requirements = [
            (category,
             (HardSexTubeCategoryStraight, HardSexTubeCategoryGay,
              HardSexTubeCategoryTranssexual), InvalidCategory),
            (tags, HardSexTubeTag, InvalidTag),
            (title, HardSexTubeTitle, InvalidTitle),
            (description, HardSexTubeDescription, InvalidDescription)]

        self._verify_upload_requirements(requirements)

        super(
            HardSexTubeVideoUploadRequest,
            self).__init__(
            video_file=video_file,
            title=title,
            tags=tags,
            category=category,
            description=description,
            **kwargs)


class HardSexTubeVideoUploaded(VideoUploaded):
    pass

    # print tnaflix_video.get_comments()
