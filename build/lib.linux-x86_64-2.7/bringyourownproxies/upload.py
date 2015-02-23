#!/usr/bin/python
import functools 

from lxml import etree
from lxml.etree import HTMLParser,tostring

ON_SUCCESS_UPLOAD = functools.partial(lambda video_request,account : None) 
ON_FAILED_UPLOAD = functools.partial(lambda exc,video_request,account,settings : None)
