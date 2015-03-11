#!/usr/bin/python
import functools 

from formatbytes.formatbytes import FormatBytes

from clint.textui.progress import Bar as ProgressBar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from lxml import etree
from lxml.etree import HTMLParser,tostring

ON_SUCCESS_UPLOAD = functools.partial(lambda video_request,account : None) 
ON_FAILED_UPLOAD = functools.partial(lambda exc,video_request,account,settings : None)

