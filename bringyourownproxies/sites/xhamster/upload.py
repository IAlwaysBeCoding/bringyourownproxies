# -*- coding: utf-8 -*-
#!/usr/bin/python
import re
import json
import time
import sys
import traceback

import path

from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.captcha import (submit_captcha_and_wait,report_bad_captcha,
                                         get_new_recaptcha_challenge,get_recaptcha_image,
                                         CaptchaProblem)
from bringyourownproxies.errors import (InvalidVideoUploadRequest,InvalidAccount,
                                        NotLogined,FailedUpload,FailedUpdatingVideoSettings)
from bringyourownproxies.sites.upload import _Upload
from bringyourownproxies.sites.xhamster.account import XhamsterAccount
from bringyourownproxies.sites.xhamster.video import XhamsterVideoUploadRequest
from bringyourownproxies.sites.xhamster.errors import FailedChangingThumbnailId,VideoNotReadyForThumbnail

__all__ = ['XhamsterUpload']

class XhamsterUpload(_Upload):

    def start(self):

        try:
            if not isinstance(self.video_upload_request,XhamsterVideoUploadRequest):
                raise InvalidVideoUploadRequest('Invalid video_upload_request, ' \
                                        'it needs to be a XhamsterVideoUploadRequest instance')
            if not isinstance(self.account,XhamsterAccount):
                raise InvalidAccount('Invalid account, it needs to be a XhamsterAccount instance')

            if not self.account.is_logined():
                raise NotLogined('Xhamster account is not logined')

            self.call_hook('started',video_upload_request=self.video_upload_request,account=self.account)

            session = self.account.http_settings.session
            proxy = self.account.http_settings.proxy
            session.headers.update({"X-Requested-With":"XMLHttpRequest"})

            title = self.video_upload_request.title
            description = self.video_upload_request.description
            categories = self.video_upload_request.category
            is_private = self.video_upload_request.is_private
            password = self.video_upload_request.password
            video_file = self.video_upload_request.video_file

            captcha_response,recaptcha_challenge = self._solve_captcha()
            upload_id = self._get_upload_id()
            self._start_upload(upload_id=upload_id)

            if not isinstance(categories,(list,tuple)):
                categories = [categories]

            fields = []
            fields.append(('title',str(title.name)))
            fields.append(('descr',str(description.name)))
            fields.append(('chanell',''))
            fields.append(('secured','1' if is_private else '0'))
            fields.append(('secured_password',password))
            fields.append(('secured_tips',''))
            fields.append(('video',(path.Path(video_file).name,open(video_file,'rb'))))
            fields.append(('recaptcha_challenge_field',recaptcha_challenge))
            fields.append(('recaptcha_response_field',captcha_response))
            for category in categories:
                fields.append(('channels[{c}]'.format(c=category.category_id),str(category.category_id)))

            encoder = type(self).create_multipart_encoder(fields)

            self.upload_monitor = type(self).create_multipart_monitor(encoder=encoder,callback=self._hooks['uploading'])

            self.call_hook('uploading',video_upload_request=self.video_upload_request,account=self.account)
            url = 'http://upload2.xhamster.com/cgi-bin/ubr_upload.6.8.pl?upload_id={upload_id}'.format(upload_id=upload_id)
            attempt_upload = session.post(url,
                                        data=self.upload_monitor,
                                        proxies=proxy,
                                        headers={'Content-Type': self.upload_monitor.content_type})

            found_after_upload = re.search(r"UberUpload.redirectAfterUpload\('(.*?)',",attempt_upload.content)
            if not found_after_upload:
                raise FailedUpload('Could not find after upload redirect url from xhamster.com')

            url = found_after_upload.group(1)
            follow_redirect = session.get(url,proxies=proxy)
            if "Your video was successfully uploaded" not in follow_redirect.content:
                raise FailedUpload('Failed uploading xhamster video after uploading video, no success message was found')

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
                            settings={})

            return {'status':True}
            #return {'status':True,'video_id':upload_request'video_id']}

    def _solve_captcha(self):

        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy

        session.headers.update({"X-Requested-With":"XMLHttpRequest"})
        title = self.video_upload_request.title.name
        description = self.video_upload_request.description.name
        categories = self.video_upload_request.category
        is_private = self.video_upload_request.is_private
        password = self.video_upload_request.password
        captcha_solver = self.video_upload_request.captcha_solver
        maximum_waiting_time = self.video_upload_request.maximum_waiting_time

        recaptcha_key = self.video_upload_request.RECAPTCHA_KEY
        video_name = path.Path(self.video_upload_request.video_file).name

        if not isinstance(categories,(list,tuple)):
            categories = [categories]

        post = {'title':title,
                'descr':description,
                'chanell':'',
                'secured':'1' if is_private else '0',
                'secured_password':password,
                'secured_tips':'',
                'video':'C:\\fakepath\\'+str(video_name)}

        for category in categories:
            post['channels[{c}]'.format(c=category.category_id)] = str(category.category_id)

        captcha_tries = 0
        captcha_maximum_tries = 5
        captcha_success = False

        while (not captcha_success) or (captcha_tries == captcha_maximum_tries):
            recaptcha_challenge = get_new_recaptcha_challenge(key=recaptcha_key)
            captcha_image = get_recaptcha_image(challenge=recaptcha_challenge)
            try:
                captcha_id,captcha_response = submit_captcha_and_wait(captcha_image,
                                                           maximum_waiting_time=maximum_waiting_time,
                                                           captcha_solver=captcha_solver,
                                                           return_captcha_id=True)
            except:
                captcha_tries += 1
            else:
                post['recaptcha_challenge_field'] = recaptcha_challenge
                post['recaptcha_response_field'] = captcha_response

                ajax_upload = session.post('http://upload2.xhamster.com/photos/ajax.php?ajax=1&act=uploadVideo&id=1',
                                                     data=post,
                                                     proxies=proxy)

                if 'Recaptcha does not match, please try again' in ajax_upload.content:
                    report_bad_captcha(captcha_solver=captcha_solver,captcha_id=captcha_id)
                    captcha_tries += 1
                else:
                    captcha_success = True

        if not captcha_success:
            raise CaptchaProblem('Unable to get a success captcha response, failed {t} times ' \
                                 'and reached maximum amount of retries'.format(t=captcha_maximum_tries))

        del session.headers['X-Requested-With']

        return (captcha_response,recaptcha_challenge)

    def _get_upload_id(self):

        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy
        url = 'http://upload2.xhamster.com/photos/uploader2/user.prepare.php?_={t}'.format(t=self._timestamp())
        prepare = session.get(url,proxies=proxy)
        found_upload_id = re.search(r'UberUpload.startUpload\("(.*?)",',prepare.content)
        if not found_upload_id:
            raise FailedUpload('Failed uploading video to xhamster because no uberupload id could be retrieved')
        return found_upload_id.group(1)

    def _start_upload(self,upload_id):

        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy
        url = 'http://upload2.xhamster.com/photos/uploader2/user.start.php?' \
            'upload_id={upload_id}&_={t}'.format(upload_id=upload_id,t=self._timestamp())

        start_upload = session.get(url,proxies=proxy)

    def _timestamp(self):
        return int(round(time.time() * 1000))
    @staticmethod
    def update_video_settings(settings,video_id,account):
        session = account.http_settings.session
        proxy = account.http_settings.proxy
        session.headers.update({"X-Requested-With":"XMLHttpRequest"})

        if not account.is_logined():
            raise NotLogined('Xhamster account is not logined')

        post =  {"videoedit[title]":settings['title'],
                "videoedit[description]":settings['description'],
                "videoedit[tags]":settings['tags'],
                "videoedit[pornstars]":settings['porn_stars'],
                "videoedit[video_options_private]":settings['is_private'],
                "videoedit[video_options_password]":settings['password'],
                "videoedit[video_options_disable_commenting]":settings['allow_comments'],
                "videoedit[uploader_category_id]":settings['category_id'],
                "videoedit[orientation]":settings['orientation']}

        url = 'http://www.xhamster.com/change/video/{videoId}/'.format(videoId=video_id)
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
            raise FailedUpdatingVideoSettings('Unknown status:{s}'.format(s=update_settings.content))

    @staticmethod
    def get_thumb_nails(video_id,account):

        session = account.http_settings.session
        proxy = account.http_settings.proxy

        if not account.is_logined():
            raise NotLogined('Xhamster account is not logined')
        go_to_thumbnails = session.get('http://www.xhamster.com/myuploads/edit/thumbnails',proxies=proxy)

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
            raise NotLogined('Xhamster account is not logined')

        url = 'http://www.xhamster.com/change/video-thumbnail/' \
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

