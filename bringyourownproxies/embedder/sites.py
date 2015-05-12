from lxml import etree
from lxml.etree import HTMLParser

from bringyourownproxies.sites import YouPornVideoParser

def youporn(html):
    parser = YouPornVideoParser()
    stats = parser.get_video_stats(html)
    return stats
