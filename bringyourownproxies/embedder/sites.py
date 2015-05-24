from functools import partial

from bringyourownproxies.sites import (YouPornVideoParser,MotherlessParser,
                                       DrTuberParser,RedTubeParser,PornhubParser)
from bringyourownproxies.embedder.errors import VideoGrabberProblem

def get_stats(site,html,get='stats',**kwargs):
    if site == 'motherless':
        parser = MotherlessParser()
    elif site == 'youporn':
        parser = YouPornVideoParser()
    elif site == 'drtuber':
        parser = DrTuberParser()
    elif site == 'redtube':
        parser = RedTubeParser()
    elif site == 'pornhub':
        parser = PornhubParser()

    print 'site:{s}'.format(s=site)
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
