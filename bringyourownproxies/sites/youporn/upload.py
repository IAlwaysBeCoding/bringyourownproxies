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
from bringyourownproxies.sites.upload import _Upload
from bringyourownproxies.sites.youporn.errors import VideoNotReadyForThumbnail,FailedChangingThumbnailId
from bringyourownproxies.sites.youporn.account import YouPornAccount
from bringyourownproxies.sites.youporn.video import YouPornVideoUploadRequest

__all__ = ['YouPornUpload']

class YouPornUpload(_Upload):

    def start(self):

        try:
            if not isinstance(self.video_upload_request,YouPornVideoUploadRequest):
                raise InvalidVideoUploadRequest('Invalid video_upload_request, ' \
                                        'it needs to be a YouPornVideoUploadRequest instance')

            if not isinstance(self.account,YouPornAccount):
                raise InvalidAccount('Invalid account, it needs to be a YouPornAccount instance')


            if not self.account.is_logined():
                raise NotLogined('YouPorn account is not logined')

            upload_requested = self._prepare_upload()
            self.call_hook('started',video_upload_request=self.video_upload_request,account=self.account)

            user_uploader_id = upload_requested['user_uploader_id']
            video_id = upload_requested['video_id']

            callback_url = upload_requested['callback_url']

            session = self.account.http_settings.session
            proxy = self.account.http_settings.proxy
            session.headers.update({"X-Requested-With":"XMLHttpRequest"})

            video_file = self.video_upload_request.video_file

            encoder = type(self).create_multipart_encoder(fields={'userId':str(user_uploader_id),
                                                                    'videoId': str(video_id),
                                                                    'callbackUrl':str(callback_url),
                                                                    'files': (path.Path(video_file).name,open(video_file, 'rb'))})

            self.upload_monitor = type(self).create_multipart_monitor(encoder=encoder,callback=self._hooks['uploading'])

            self.call_hook('uploading',video_upload_request=self.video_upload_request,account=self.account)

            attempt_upload = session.post('http://www.youporn.com/videouploading',
                                        data=self.upload_monitor,
                                        proxies=proxy,
                                        headers={'Content-Type': self.upload_monitor.content_type})

            del session.headers['X-Requested-With']

            settings = self.video_upload_request.create_video_settings()
            do_callback = session.get(callback_url,proxies=proxy)

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
                            settings={'video_id':upload_requested['video_id']})

            return {'status':True,'video_id':upload_requested['video_id']}

    def _prepare_upload(self):

        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy

        if not self.account.is_logined():
            raise NotLogined('YouPorn account is not logined')

        upload_page = session.get('http://www.youporn.com/upload',proxies=proxy)
        doc = etree.fromstring(upload_page.content,HTMLParser())
        callback_url = doc.xpath('//input[@name="callbackUrl"]/@value')[0]

        session.headers.update({"X-Requested-With":"XMLHttpRequest",
                                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"})


        video_size = os.path.getsize(self.video_upload_request.video_file)
        video = path.Path(self.video_upload_request.video_file)
        post = {'file':video.name,'size':video_size}

        create_upload_request = session.post('http://www.youporn.com/upload/create-videos/',data=post,proxies=proxy)

        response = json.loads(create_upload_request.content)
        if 'success' in response:
            if not response['success']:
                raise FailedUpload('Failed to upload video reason:{reason}'.format(reason=response['reason']))

        del session.headers['X-Requested-With']
        response['callback_url'] = callback_url
        return response

    @staticmethod
    def update_video_settings(settings,video_id,account):
        session = account.http_settings.session
        proxy = account.http_settings.proxy
        session.headers.update({"X-Requested-With":"XMLHttpRequest"})

        if not account.is_logined():
            raise NotLogined('YouPorn account is not logined')

        post =  {"videoedit[title]":settings['title'],
                "videoedit[description]":settings['description'],
                "videoedit[tags]":settings['tags'],
                "videoedit[pornstars]":settings['porn_stars'],
                "videoedit[video_options_private]":settings['is_private'],
                "videoedit[video_options_password]":settings['password'],
                "videoedit[video_options_disable_commenting]":settings['allow_comments'],
                "videoedit[uploader_category_id]":settings['category_id'],
                "videoedit[orientation]":settings['orientation']}

        url = 'http://www.youporn.com/change/video/{videoId}/'.format(videoId=video_id)
        update_settings = session.post(url,data=post,proxies=proxy)
        response = json.loads(update_settings.content)
        del session.headers['X-Requested-With']
        if 'success' in response:
            if not response['success']:
                errors = []
                for key in response['errors']:
                    errors.append("{k} = {v}".format(k=key,v=response['errors'][key]))

                raise FailedUpdatingVideoSettings('Failed updating video settings errors:{e}'.format(",".join(errors)))
            else:
                return True
        else:
            raise FailedUpdatingVideoSettings('Unknown status:{s}'.format(s=update_video_settings.content))

    @staticmethod
    def get_thumb_nails(video_id,account):

        session = account.http_settings.session
        proxy = account.http_settings.proxy

        if not account.is_logined():
            raise NotLogined('YouPorn account is not logined')
        go_to_thumbnails = session.get('http://www.youporn.com/myuploads/edit/thumbnails',proxies=proxy)

        xpath = '//div[@class="pickThumbnails content-box grid_15"]//div[@class="videoRow"]'
        doc = etree.fromstring(go_to_thumbnails.content,HTMLParser())
        get_videos = doc.xpath(xpath)

        found_video = False
        for div in get_videos:
            current_video_id = div.attrib['id'].replace('videoRow_','')
            if str(current_video_id) == str(video_id):
                vid_doc = etree.fromstring(tostring(div),HTMLParser())

                xpath = '//div[@class="rightContainer"]//div[@class="thumbnailGrid/div[@class="selectThumbnail"]'
                get_thumbnails = vid_doc.xpath(xpath)

                thumbnails = []

                for thumbnail in get_thumbnails:
                    current_thumbnail_id = thumbnail.attrib['data-thumbnail']

                    thumb_doc = etree.fromstring(tostring(thumbnail),HTMLParser())

                    img_src = thumb_doc.xpath('//img[@src]')[0]
                    thumbnails.append((current_thumbnail_id,img_src.attrib['src']))
                break

        if not found_video:
            raise VideoNotReadyForThumbnail('Video not ready for thumbnail change')

        else:
            return thumbnails

    @staticmethod
    def pick_thumb_nail(video_id,account,thumbnail_id=1):

        session = account.http_settings.session
        proxy = account.http_settings.proxy

        if not account.is_logined():
            raise NotLogined('YouPorn account is not logined')

        url = 'http://www.youporn.com/change/video-thumbnail/' \
            '{videoId}/{thumbnailId}/'.format(videoId=video_id,thumbnailId=thumbnail_id)

        post = {'video_id':video_id,'selectedThumbnail':thumbnail_id}
        update_thumbnail = session.post(url,data=post,proxies=proxy)

        response = json.loads(update_thumbnail.content)
        if 'status' in response:
            if response['status'] == 'error':
                raise FailedChangingThumbnailId('Failed Changing thumbnail_' \
                                                'id:{t} on video_id:{v} message:' \
                                                '{msg}'.format(t=thumbnail_id,v=video_id,msg=response['message']))
        else:
            raise FailedChangingThumbnailId('Failed Changing thumbnail_' \
                                            'id:{t} on video_id:{v}'.format(t=thumbnail_id,v=video_id))

        return True

