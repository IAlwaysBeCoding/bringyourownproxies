#!/usr/bin/python
import os
import json
import sys
import traceback

import path

from requests_toolbelt import MultipartEncoder
from lxml import etree
from lxml.etree import HTMLParser,tostring
from bringyourownproxies.errors import (InvalidVideoUploadRequest,InvalidAccount,
                                        NotLogined,FailedUpload,FailedUpdatingVideoSettings)
from bringyourownproxies.upload import Upload


#from errors import VideoNotReadyForThumbnail,FailedChangingThumbnailId
#from account import YouPornAccount
#from video import YouPornVideoUploadRequest