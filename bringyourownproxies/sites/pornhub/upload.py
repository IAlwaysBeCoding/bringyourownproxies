#!/usr/bin/python
import sys
import traceback
import time 

import path

from requests.cookies import create_cookie
from requests_toolbelt import MultipartEncoder
from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.errors import (InvalidVideoUploadRequest,InvalidAccount,NotLogined,
                                        InvalidTitle,FailedUpload)

from bringyourownproxies.sites.upload import _Upload
from bringyourownproxies.sites.pornhub.errors import CannotFindCookie
from bringyourownproxies.sites.pornhub.account import PornhubAccount
from bringyourownproxies.sites.pornhub.video import PornhubVideoUploadRequest

__all__ = ['PornhubUpload']

class PornhubUpload(_Upload):

    def start(self):

        try:
            if not isinstance(self.video_upload_request,PornhubVideoUploadRequest):
                raise InvalidVideoUploadRequest('Invalid video_upload_request, ' \
                                        'it needs to be a PornhubVideoUploadRequest instance')
                                        
            if not isinstance(self.account,PornhubAccount):
                raise InvalidAccount('Invalid account, it needs to be a PornhubAccount instance')
            
            
            if not self.account.is_logined():
                raise NotLogined('Pornhub account is not logined')
            
            self.call_hook('started',video_upload_request=self.video_upload_request,account=self.account)

            session = self.account.http_settings.session
            proxy = self.account.http_settings.proxy
            
            
            
            go_to_upload = session.get('http://www.pornhub.com/upload/video',proxies=proxy)
            session.headers.update({"X-Requested-With":"XMLHttpRequest"})
            
            container = go_to_upload.content.\
                                        split('<div class="saveBlockContent">')[1].\
                                        split('</div><!-- /.saveBlockContent -->')[0]
            container = "".join(['<div class="saveBlockContent">',container,'</div>'])
            
            fields = []
            
            
            
            doc = etree.fromstring(container,HTMLParser())
            get_cookie = doc.xpath('//input[@name="cookie[]"]/@value')
            if len(get_cookie) == 0:
                raise CannotFindCookie('Cannot find input field with name:cookies[]')
            self.upload_monitor = type(self).create_multipart_monitor(encoder=encoder,callback=self._hooks['uploading'])                                                

            self.call_hook('uploading',video_upload_request=self.video_upload_request,account=self.account)            
            
            
                
        except Exception as exc:

            self.call_hook('failed',video_upload_request=self.video_upload_request,
                                    account=self.account,
                                    traceback=traceback.format_exc(),
                                    exc_info=sys.exc_info())

            if self.bubble_up_exception:
                raise exc
        
        else:

            self.call_hook('finished',
                            video_request=self.video_upload_request,
                            account=self.account,
                            settings={''})
            
            return {'status':True}

