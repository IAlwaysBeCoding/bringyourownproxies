# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import traceback
import re

import path

from lxml import etree
from lxml.etree import HTMLParser

from bringyourownproxies.errors import (InvalidVideoUploadRequest,InvalidAccount,NotLogined,
                                        FailedUpload,CannotFindVar,FailedUpdatingVideoSettings)

from bringyourownproxies.sites.upload import _Upload
from bringyourownproxies.sites.xvideos.account import XvideosAccount
from bringyourownproxies.sites.xvideos.video import XvideosVideoUploadRequest

__all__ = ['XvideosUpload']

class XvideosUpload(_Upload):

    def start(self):

        try:
            if not isinstance(self.video_upload_request,XvideosVideoUploadRequest):
                raise InvalidVideoUploadRequest('Invalid video_upload_request, ' \
                                        'it needs to be a XvideosVideoUploadRequest instance')

            if not isinstance(self.account,XvideosAccount):
                raise InvalidAccount('Invalid account, it needs to be a XvideosAccount instance')

            if not self.account.is_logined():
                raise NotLogined('Xvideos account is not logined')

            self.call_hook('started',video_upload_request=self.video_upload_request,account=self.account)

            session = self.account.http_settings.session
            proxy = self.account.http_settings.proxy

            go_to_upload = session.get('http://upload.xvideos.com/account/uploads/new',proxies=proxy)

            doc = etree.fromstring(go_to_upload.content,HTMLParser())

            get_apc_upload_progress = doc.xpath('//input[@name="APC_UPLOAD_PROGRESS"]/@value')

            if len(get_apc_upload_progress) == 0:
                raise CannotFindVar('Cannot find input field with name:APC_UPLOAD_PROGRESS')

            video_file = self.video_upload_request.video_file
            tags = self.video_upload_request.tags

            if isinstance(tags,(tuple,list)):
                tags = " ".join([t.name for t in tags])
            else:
                tags = tags.name

            fields = []

            fields.append(('APC_UPLOAD_PROGRESS',get_apc_upload_progress[0]))
            fields.append(('message',''))
            fields.append(('tags',tags))
            fields.append(('upload_file',(path.Path(video_file).name,open(video_file, 'rb'))))
            encoder = type(self).create_multipart_encoder(fields)

            self.upload_monitor = type(self).create_multipart_monitor(encoder=encoder,callback=self._hooks['uploading'])

            self.call_hook('uploading',video_upload_request=self.video_upload_request,account=self.account)

            url = 'http://upload.xvideos.com/account/uploads/submit?video_type=other'
            upload_video = session.post(url,
                                        data=self.upload_monitor,
                                        proxies=proxy,
                                        headers={'Content-Type': self.upload_monitor.content_type})
            doc = etree.fromstring(upload_video.content,HTMLParser())
            find_error = doc.xpath('//span[@class="inlineError"]')
            if find_error:
                error = find_error[0].text
                raise FailedUpload('Upload failed in xvideos.com error:{error}'.format(error=error))
            else:
                if doc.xpath('//span[@class="ok"'):
                    get_video_id = doc.xpath('//a[@target="_top"]')
                    if get_video_id:
                        url = get_video_id[0].attrib['href']
                        find_video_id = re.match(r'/account/uploads/(.*?)/edit',url)
                        if find_video_id:
                            video_id = find_video_id.group(1)
                    raise CannotFindVar('Cannot find video id after finishing uploading video')

                raise FailedUpload('Unknown status,failed uploading to xvideos')
            settings = self.video_upload_request.create_video_settings()
            type(self).update_video_settings(settings,video_id,self.account)
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
                            settings={'video_id':video_id})

            return {'status':True}

    @staticmethod
    def update_video_settings(settings,video_id,account):

        session = account.http_settings.session
        proxy = account.http_settings.proxy

        if not account.is_logined():
            raise NotLogined('YouPorn account is not logined')
        url = 'http://upload.xvideos.com/account/uploads/{videoId}/edit'.format(videoId=video_id)

        session.get(url,proxies=proxy)
        post =  {"title]":settings['title'],
                "description]":settings['description'],
                "hide":settings['is_private'],
                "keywords":settings['tags'],
                "update_video_information":"update_video_information"}
        update_settings = session.post(url,data=post,proxies=proxy)
        doc = etree.fromstring(update_settings.content,HTMLParser())
        find_ok = doc.xpath('//p[@class="inlineOK"]')
        if find_ok:
            find_txt = 'Your modifications have been saved.'
            if find_ok[0].text != find_txt:
                raise FailedUpdatingVideoSettings('Possible failed updating settings.'\
                                                    'success string was not found:{s}'.format(s=find_txt))
            return True
        else:
            find_error = doc.xpath('//p[@class="inlineError"]')
            if find_error:
                error = find_error[0].text
                raise FailedUpdatingVideoSettings('Failed updating video settings due to error:{err}'.format(err=error))

            raise FailedUpdatingVideoSettings('Unknown error while updating video settings')
