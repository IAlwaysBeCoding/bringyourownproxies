from functools import partial

from bringyourownproxies.sites import (YouPornParser,MotherlessParser,
                                       DrTuberParser,RedTubeParser,
                                       PornhubParser,XvideosParser)
from bringyourownproxies.embedder.errors import VideoGrabberProblem

def get_stats(site,html,get='stats',**kwargs):
    if site == 'motherless':
        parser = MotherlessParser()
    elif site == 'youporn':
        parser = YouPornParser()
    elif site == 'drtuber':
        parser = DrTuberParser()
    elif site == 'redtube':
        parser = RedTubeParser()
    elif site == 'pornhub':
        parser = PornhubParser()
    elif site == 'xvideos':
        parser = XvideosParser()

    if get == 'stats':
        result = parser.get_video_stats(html,**kwargs)
    elif get == 'download':
        result = parser.get_download_url(html,**kwargs)
    else:
        raise VideoGrabberProblem('Unknown info to get' \
                                  'you can either ' \
                                  'get stats or download url')
    return result

youporn = partial(get_stats,site='youporn')
motherless = partial(get_stats,site='motherless')
drtuber = partial(get_stats,site='drtuber')
redtube = partial(get_stats,site='redtube')
pornhub = partial(get_stats,site='pornhub')
xvideos = partial(get_stats,site='xvideos')
