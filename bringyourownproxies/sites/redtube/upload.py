# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import traceback
import json
import re
import random

import path

from bringyourownproxies.errors import (
    InvalidVideoUploadRequest,
    InvalidAccount,
    NotLogined,
    FailedUpload,
    CannotFindVar)

from bringyourownproxies.utils import generate_timestamp
from bringyourownproxies.sites.upload import _Upload
from bringyourownproxies.sites.redtube.account import RedTubeAccount
from bringyourownproxies.sites.redtube.video import RedTubeVideoUploadRequest

__all__ = ['RedTubeUpload']


class RedTubeUpload(_Upload):

    def start(self):

        try:
            if not isinstance(self.video_upload_request, RedTubeVideoUploadRequest):
                raise InvalidVideoUploadRequest(
                    'Invalid video_upload_request, '
                    'it needs to be a RedTubeVideoUploadRequest instance')

            if not isinstance(self.account, RedTubeAccount):
                raise InvalidAccount(
                    'Invalid account, it needs to be a RedTubeAccount instance')

            if not self.account.is_logined():
                raise NotLogined('RedTube account is not logined')

            session = self.account.http_settings.session
            proxy = self.account.http_settings.proxy
            session.get('http://www.redtube.com/uploadsplash',proxies=proxy)

            self.call_hook(
                'started',
                video_upload_request=self.video_upload_request,
                account=self.account)
            session.post('http://www.redtube.com/upload/islogged',proxies=proxy)
            self._upload()

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

    def _upload(self):

        video_file = self.video_upload_request.video_file
        tags = self.video_upload_request.tags
        title = self.video_upload_request.title
        is_private = self.video_upload_request.is_private

        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy

        session.headers.update({'X-Requested-With':'X-Requested-With:ShockwaveFlash/17.0.0.134',
                                'Referer':'http://www.redtube.com/upload'})
        go_to_upload = session.get(
            'http://www.redtube.com/upload',
            proxies=proxy)

        def generate_char(chars):
            clean = []
            u_l = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            l_l = 'abcdefghijklmnopqrstuvwxyz'
            num = '1234567890'
            for char in chars:
                if char == 'U':
                    clean.append(random.choice(u_l))
                elif char == 'N':
                    clean.append(random.choice(num))
                elif char == 'L':
                    clean.append(random.choice(l_l))
                else:
                    clean.append(char)

            return "".join(clean)

        def generate_pow_upload_id():
            chars = 'BUNUUNUU-NNNN-NUBU-NNNN-BNNNBUU1UBUN'
            return generate_char(chars)

        def generate_file_id():
            chars = 'NNUNNNUUN-NNNN-NUUU-UNNN-NNNUNNNNNUUN'
            return generate_char(chars)

        def get_redtube_cookies():
            cookies = []
            redtube_cookies = session.cookies._cookies['.redtube.com']
            for path in redtube_cookies:
                for raw_cookie in redtube_cookies[path]:
                    c = redtube_cookies[path][raw_cookie]
                    cookies.append('{k}={v}'.format(k=c.name, v=c.value))
            return "; ".join(cookies)
        def generate_timestamp_mil():
            tm = generate_timestamp()
            mil = random.randrange(1000,9999,1)
            return '{tm}{mil}'.format(tm=tm,mil=mil)

        cookies = get_redtube_cookies()
        fields = []
        fields.append(('Upload', str('Submit Query')))
        fields.append(('currentFileIndex', str('0')))
        fields.append(('fileModificationDate', str(generate_timestamp_mil())))
        fields.append(('fileCreationdate', str(generate_timestamp_mil())))
        fields.append(('fileId', str(generate_file_id())))
        fields.append(('fileSize', str(path.Path(video_file).getsize())))
        fields.append(('tags', str('|'.join([t.name for t in tags]))))
        fields.append(('filesCount', str('1')))
        fields.append(('type', '2' if is_private else '1'))
        fields.append(('title', title.name))
        fields.append(('MultiPowUpload_browserCookie',str(cookies)))
        fields.append(('MultiPowUploadId', str(generate_pow_upload_id())))
        fields.append(('Filename', str(path.Path(video_file).name)))
        fields.append(
                ('Filedata',
                 (path.Path(video_file).name,
                  open(
                      video_file,
                      'rb'))))

        encoder = type(self).create_multipart_encoder(fields)
        self.upload_monitor = type(self).create_multipart_monitor(encoder)

        find_upload_url = re.search(
            r'var\s+uploadUrl\s+=\s+"(.*?)";',
            go_to_upload.content)

        if not find_upload_url:
            raise CannotFindVar('Unable to find upload url for redtube.com')

        session_id = find_upload_url.group(1)
        url = 'http://www.redtube.com/upload/file?upload_session={s}'.format(
            s=session_id)

        upload_video = session.post(
            url,
            data=self.upload_monitor,
            proxies=proxy,
            headers={'Content-Type':self.upload_monitor.content_type})

        response = json.loads(upload_video.content.replace('/* upload response */',''))
        if not response['success']:
            if 'error' in response:
                error = response['error']
            elif 'errorBox' in response:
                error = response['errorBox']
            raise FailedUpload('Redtube failed upload due to error:{e}'.format(e=error))
        return True
