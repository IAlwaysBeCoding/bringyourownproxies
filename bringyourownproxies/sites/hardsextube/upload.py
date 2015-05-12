#!/usr/bin/python
import sys
import traceback
import random
import path

from ua_parser import user_agent_parser
from lxml import etree
from lxml.etree import HTMLParser

from bringyourownproxies.errors import (
    InvalidVideoUploadRequest,
    InvalidAccount,
    NotLogined,
    FailedUpload,
    CannotFindVar,
    InvalidThumbnailId,
    InvalidCategory)

from bringyourownproxies.sites.upload import _Upload
from bringyourownproxies.sites.hardsextube.account import HardSexTubeAccount
from bringyourownproxies.sites.hardsextube.video import HardSexTubeVideoUploadRequest
from bringyourownproxies.sites.hardsextube.properties import (HardSexTubeCategoryStraight,
                                                            HardSexTubeCategoryGay,
                                                            HardSexTubeCategoryTranssexual)

__all__ = ['HardSexTubeUpload']

class HardSexTubeUpload(_Upload):

    def start(self):

        try:
            if not isinstance(self.video_upload_request, HardSexTubeVideoUploadRequest):
                raise InvalidVideoUploadRequest(
                    'Invalid video_upload_request, '
                    'it needs to be a HardSexTubeVideoUploadRequest instance')

            if not isinstance(self.account, HardSexTubeAccount):
                raise InvalidAccount(
                    'Invalid account, it needs to be a HardSexTubeAccount instance')

            if not self.account.is_logined():
                raise NotLogined('HardSexTube account is not logined')

            session = self.account.http_settings.session
            proxy = self.account.http_settings.proxy

            video_file = self.video_upload_request.video_file
            tags = self.video_upload_request.tags
            title = self.video_upload_request.title
            description = self.video_upload_request.description
            tags = self.video_upload_request.tags
            porn_star = self.video_upload_request.porn_star
            thumbnail_id = self.video_upload_request.thumbnail_id
            category = self.video_upload_request.category
            if isinstance(category,HardSexTubeCategoryStraight):
                orientation = 'straight'
            elif isinstance(category,HardSexTubeCategoryGay):
                orientation = 'gay'
            elif isinstance(category,HardSexTubeCategoryTranssexual):
                orientation = 'tranny'
            else:
                raise InvalidCategory('Hardsextube category needs to be straight' \
                                      ' gay or transsexual')
            self.call_hook(
                'started',
                video_upload_request=self.video_upload_request,
                account=self.account)

            go_to_upload_center = session.get(
                'http://uploadcenter.hardsextube.com/',
                proxies=proxy)

            doc = etree.fromstring(go_to_upload_center.content,HTMLParser())
            found_upload_id = doc.xpath('//input[@name="upload_id"]/@value')

            if not found_upload_id:
                raise CannotFindVar('Unable to find upload_id for hardsextube upload')

            upload_id = found_upload_id[0]

            thumbnail_ids = self._upload(video_file,upload_id)
            if int(thumbnail_id) > len(thumbnail_ids):
                raise InvalidThumbnailId('Invalid thumbnail_id:{i} for HardSexTube video'.format(i=thumbnail_id))

            self._log_start(upload_id)
            self._log_client(upload_id)

            self._submit_upload('form_validation',
                                upload_id,
                                title,
                                description,
                                orientation,
                                category,
                                tags,
                                porn_star,
                                thumbnail_id)
            self._submit_upload('store',
                                upload_id,
                                title,
                                description,
                                orientation,
                                category,
                                tags,
                                porn_star,
                                thumbnail_id)

        except Exception as exc:

            self.call_hook(
                'failed',
                video_upload_request=self.video_upload_request,
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

            return {'status': True}


    def _upload(self,video_file,upload_id):

        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy

        fields = []
        fields.append(('upload_id',str(upload_id)))
        fields.append(('upload_url',''))
        fields.append(
                ('video',
                 (path.Path(video_file).name,
                  open(
                      video_file,
                      'rb'))))

        encoder = type(self).create_multipart_encoder(fields)
        self.upload_monitor = type(self).create_multipart_monitor(encoder,self._hooks['uploading'])

        url = 'http://uploadcenter.hardsextube.com/fileupload'
        upload_video = session.post(
            url,
            data=self.upload_monitor,
            proxies=proxy,
            headers={'Content-Type':self.upload_monitor.content_type})

        response = upload_video.json()

        if not response['success']:
            error = response['message']
            raise FailedUpload('HardSexTube failed upload due to error:{e}'.format(e=error))
        return  response['thumbs']

    def _submit_upload(self,upload_type,
                            upload_id,
                            title,
                            description,
                            orientation,
                            category,
                            tags,
                            porn_star,
                            thumbnail_id):

        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy

        categories = []
        if isinstance(category,(list,tuple)):
            categories = [c.category_id for c in category]
        else:
            categories = [category.category_id]

        if not isinstance(tags,(list,tuple)):
            tags = [tags]

        fields = []
        fields.append(('upload_id',str(upload_id)))
        fields.append(('title',str(title.name)))
        fields.append(('description',str(description.name)))
        fields.append(('text_ad_title',''))
        fields.append(('text_ad_url',''))
        fields.append(('orientation',str(orientation)))
        fields.append(('tags',','.join([t.name for t in tags])))
        fields.append(('pornstars',str(porn_star) if porn_star else ''))
        fields.append(('default_thumb',str(thumbnail_id)))
        for c in categories:
            fields.append(('categories[]',str(c)))

        encoder = type(self).create_multipart_encoder(fields)
        self.upload_monitor = type(self).create_multipart_monitor(encoder)
        if upload_type == 'form_validation':
            url = 'http://uploadcenter.hardsextube.com/upload/form-validation'
            post = {}
            for f in fields:
                key,value = f
                if key not in post:
                    post[key] = value
            h = {}
        elif upload_type == 'store':
            url = 'http://uploadcenter.hardsextube.com/upload/store'
            post = self.upload_monitor
            h = {'Content-Type':self.upload_monitor.content_type}
        else:
            raise FailedUpload('Invalid upload_type, it can either be form_validation or sort')

        session.headers.update({'Origin':'http://uploadcenter.hardsextube.com',
                                'Referer':'http://uploadcenter.hardsextube.com/',
                                })
        form_validate = session.post(url,
                                     data=post,
                                     proxies=proxy,
                                     headers=h if h else None)

    def _log_start(self,upload_id):

        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy

        url = 'http://uploadcenter.hardsextube.com/upload/log-start'
        post = {'uploadId':upload_id}

        start_log = session.post(url,data=post,proxies=proxy)
        response = start_log.json()
        if not response['success']:
            raise FailedUpload('HardSexTube log start failed')

    def _log_client(self,upload_id):

        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy

        ua_info = user_agent_parser.Parser(self.account.http_settings.user_agent)
        family = ua_info['os']['family']
        browser = ua_info['user_agent']['family']
        url = 'http://uploadcenter.hardsextube.com/upload/log-client-info'
        post = {'uploadId':str(upload_id),
                'clientInfo[browser]':browser,
                'clientInfo[fullversion]':'/41.0.2272.118 Safari/537.36',
                'clientInfo[navigator]':'Netscape',
                'clientInfo[navigatorUser]':str(self.account.http_settings.user_agent),
                'clientInfo[OSName]':'UNIX' if 'linux' in family else 'WIN',
                'clientInfo[screenW]':random.choice([1440,1920,1366,1280,1024]),
                'clientInfo[screenH]':random.choice([876,1080,768,800,600]),
                'clientInfo[winW]':random.choice([1360,1312,984,780]),
                'clientInfo[winH]':random.choice([478,506,578,6340])}
        client_log = session.post(url,data=post,proxies=proxy)
        response = client_log.json()
        if not response['success']:
            raise FailedUpload('HardSexTube log start failed')



