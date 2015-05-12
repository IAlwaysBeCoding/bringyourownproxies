#!/usr/bin/python
import sys
import traceback
import re

import path

from lxml import etree
from lxml.etree import HTMLParser

from bringyourownproxies.errors import (
    InvalidVideoUploadRequest,
    InvalidAccount,
    NotLogined,
    FailedUpload,
    CannotFindVar)

from bringyourownproxies.utils import generate_timestamp
from bringyourownproxies.sites.upload import _Upload
from bringyourownproxies.sites.pornhub.account import PornhubAccount
from bringyourownproxies.sites.pornhub.video import PornhubVideoUploadRequest

__all__ = ['PornhubUpload']

class PornhubUpload(_Upload):

    def start(self):

        try:
            if not isinstance(self.video_upload_request, PornhubVideoUploadRequest):
                raise InvalidVideoUploadRequest(
                    'Invalid video_upload_request, '
                    'it needs to be a PornhubVideoUploadRequest instance')

            if not isinstance(self.account, PornhubAccount):
                raise InvalidAccount(
                    'Invalid account, it needs to be a PornhubAccount instance')

            if not self.account.is_logined():
                raise NotLogined('Pornhub account is not logined')

            self.call_hook(
                'started',
                video_upload_request=self.video_upload_request,
                account=self.account)

            session = self.account.http_settings.session
            proxy = self.account.http_settings.proxy

            go_to_upload = session.get(
                'http://www.pornhub.com/upload/video',
                proxies=proxy)
            session.headers.update({"X-Requested-With": "XMLHttpRequest"})

            container = go_to_upload.content.\
                split('<div class="saveBlockContent">')[1].\
                split('</div><!-- /.saveBlockContent -->')[0]
            container = "".join(
                ['<div class="saveBlockContent">', container, '</div>'])
            doc = etree.fromstring(container, HTMLParser())

            get_cookie = doc.xpath('//input[@name="cookie[]"]/@value')
            get_platform_id = doc.xpath('//input[@name="platformId[]"]/@value')
            get_source = doc.xpath('//input[@name="source[]"]/@value')

            if len(get_cookie) == 0:
                raise CannotFindVar(
                    'Cannot find input field with name:cookies[]')
            if len(get_platform_id) == 0:
                raise CannotFindVar(
                    'Cannot find input field with name:platformId[]')
            if len(get_source) == 0:
                raise CannotFindVar(
                    'Cannot find input field with name:source[]')

            video_file = self.video_upload_request.video_file
            title = self.video_upload_request.title.name
            tags = self.video_upload_request.tags
            category = self.video_upload_request.category
            is_private = self.video_upload_request.is_private
            is_homemade = self.video_upload_request.is_homemade
            porn_stars = self.video_upload_request.porn_stars

            if not isinstance(category, (tuple, list)):
                categories = '["{cat}"]'.format(cat=str(category.category_id))
            else:
                categories = [
                    '"{c}"'.format(
                        c=str(
                            cat.category_id)) for cat in category]
                categories = '[{cats}]'.format(cats=','.join(categories))

            if isinstance(tags, (tuple, list)):
                tags = " ".join([t.name for t in tags])

            privacy = "private" if is_private else "community"
            production = "homemade" if is_homemade else "professional"
            fields = []

            fields.append(('title', title))
            fields.append(('callbackUrl', ''))
            fields.append(('platformId', str(get_platform_id[0])))
            fields.append(('categories', categories))
            fields.append(('tags', tags))
            fields.append(('privacy', privacy))
            fields.append(('source', str(get_source[0])))
            fields.append(('pornstars', porn_stars))
            fields.append(('cookie', get_cookie[0]))
            fields.append(('production', production))
            fields.append(('timestamp', str(generate_timestamp())))
            fields.append(('isPremiumVideo', "0"))
            fields.append(
                ('Filedata',
                 (path.Path(video_file).name,
                  open(
                      video_file,
                      'rb'))))
            encoder = type(self).create_multipart_encoder(fields)

            self.upload_monitor = type(self).create_multipart_monitor(
                encoder=encoder,
                callback=self._hooks['uploading'])

            self.call_hook(
                'uploading',
                video_upload_request=self.video_upload_request,
                account=self.account)

            get_upload_url = re.search(
                r"var\s+url\s+=\s+'(.*?)',",
                go_to_upload.content)
            if not get_upload_url:
                raise CannotFindVar('Cannot find uploading url for pornhub.com')

            url = get_upload_url.group(1)
            upload_video = session.post(
                url,
                data=self.upload_monitor,
                proxies=proxy,
                headers={
                    'Content-Type': self.upload_monitor.content_type})
            find_str = '{"@type":["GorillaHub\\\SDKs\\\SDKBundle\\\V0001\\\Domain\\\Responses\\\FileUploadedResponse",[]]'
            if find_str not in upload_video.content:
                raise FailedUpload(
                    'Upload possibly failed, did not find success string:{string}'.format(
                        string=find_str))
        except Exception as exc:
            del session.headers["X-Requested-With"]
            self.call_hook(
                'failed',
                video_upload_request=self.video_upload_request,
                account=self.account,
                traceback=traceback.format_exc(),
                exc_info=sys.exc_info())

            if self.bubble_up_exception:
                raise exc

        else:
            del session.headers["X-Requested-With"]
            self.call_hook('finished',
                           video_request=self.video_upload_request,
                           account=self.account,
                           settings={''})

            return {'status': True}
