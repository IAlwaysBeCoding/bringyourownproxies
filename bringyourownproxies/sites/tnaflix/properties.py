
from bringyourownproxies.video import Title,Description,Tag,Category

__all__ = ['TnaflixTitle','TnaflixDescription','TnaflixTag','TnaflixCategory']

class TnaflixTitle(Title):
    SITE = 'Tnaflix'
    SITE_URL = 'www.tnaflix.com'

class TnaflixDescription(Description):
    SITE = 'Tnaflix'
    SITE_URL = 'www.tnaflix.com'

class TnaflixTag(Tag):
    SITE = 'Tnaflix'
    SITE_URL = 'www.tnaflix.com'

class TnaflixCategory(Category):
    SITE = 'Tnaflix'
    SITE_URL = 'www.tnaflix.com'
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
            	"milf ": "43",
            	"oral": "72",
            	"petite": "24",
            	"piss": "34",
            	"compilations": "79",
            	"pov": "29",
            	"pregnant ": "36",
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

    def __init__(self,name,**kwargs):

        self.category_id = kwargs.get('category_id',None)
        if self.category_id is None:
            get_category_id = self._find_category_id(category=name)

            if get_category_id is None:
                raise InvalidCategory('Invalid Category Name:{name}, it does not match a category id'.format(name=name))

            self.category_id = get_category_id

        super(TnaflixCategory,self).__init__(name=name,**kwargs)

    def _find_category_id(self,category):

        if category.lower() in self.CATEGORIES:
            return self.CATEGORIES[category.lower()]


