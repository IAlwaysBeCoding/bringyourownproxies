#!/usr/bin/python
import sys
import traceback

import path

from lxml import etree
from lxml.etree import HTMLParser, tostring

from bringyourownproxies.errors import (
    InvalidVideoUploadRequest,
    InvalidAccount,
    NotLogined,
    FailedUpload,
    CannotFindVar,
    InvalidThumbnailId)

from bringyourownproxies.sites.upload import _Upload
from bringyourownproxies.sites.hardsextube.account import HardSexTubeAccount
from bringyourownproxies.sites.hardsextube.video import (HardSexTubeVideoUploadRequest, HardSexTubeCategoryStraight
                                                         )


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
            else:
                orientation = 'tranny'

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
            if thumbnail_id > len(thumbnail_ids):
                raise InvalidThumbnailId('Invalid thumbnail_id:{i} for HardSexTube video'.format(i=thumbnail_id))

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
            del session.headers["X-Requested-With"]
            self.call_hook(
                'failed',
                video_upload_request=self.video_upload_request,
                account=self.account,
                traceback=traceback.format_exc(),
                exc_info=sys.exc_info())
            print traceback.format_exc()

            if self.bubble_up_exception:
                raise exc

        else:
            del session.headers["X-Requested-With"]
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
        print 'type:{t}:{p}'.format(t=upload_type,p=post)
        print 'fields:{f}'.format(f=fields)
        form_validate = session.post(url,
                                     data=post,
                                     proxies=proxy,
                                     headers=h if h else None)
        with open('{t}.html'.format(t=upload_type),'w+') as f:
            f.write(form_validate.content)

    def _store(self):
        pass

    def _get_thumbnail_options(self):
        pass
    def _set_video_thumbnail(self):
        pass

