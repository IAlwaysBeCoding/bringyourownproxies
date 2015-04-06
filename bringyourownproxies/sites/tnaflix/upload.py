#!/usr/bin/python
import os
import json
import sys
import traceback

import path

from requests_toolbelt import MultipartEncoder
from lxml import etree
from lxml.etree import HTMLParser,tostring
from bringyourownproxies.errors import InvalidVideoUploadRequest,InvalidAccount,NotLogined
from bringyourownproxies.sites.upload import _Upload,UbrUploader
from bringyourownproxies.sites.tnaflix.account import TnaflixAccount
from bringyourownproxies.sites.tnaflix.video import TnaflixVideoUploadRequest

__all__ = ['TnaflixUpload']

class TnaflixUpload(_Upload):

    def start(self,**kwargs):

        try:
            if not isinstance(self.video_upload_request,TnaflixVideoUploadRequest):
                raise InvalidVideoUploadRequest('Invalid video_upload_request, ' \
                                        'it needs to be a TnaflixVideoUploadRequest instance')
                                        
            if not isinstance(self.account,TnaflixAccount):
                raise InvalidAccount('Invalid account, it needs to be a TnaflixAccount instance')
            
            
            if not self.account.is_logined():
                raise NotLogined('Tnaflix account is not logined')

            session = self.account.http_settings.session
            proxy = self.account.http_settings.proxy

            go_to_upload = session.get('https://www.tnaflix.com/upload.php',proxies=proxy)    

            self.call_hook('started',video_upload_request=self.video_upload_request,account=self.account)
            
            if isinstance(self.video_upload_request.category,(list,tuple)):
                channel_ids = [t.category_id for t in self.video_upload_request.category]
            else:
                channel_ids = [self.video_upload_request.category.category_id]

            fields = []
                
            ready_tag_ids = [('chlist[]',str(c)) for c in channel_ids]
            fields.append(('field_myvideo_title',self.video_upload_request.title.name))
            fields.append(('field_myvideo_descr',self.video_upload_request.description.name))
            fields.append(('field_myvideo_keywords'," ".join([t.name for t in self.video_upload_request.tags])))
            fields.append(('declared','on'))
            fields.append(('action_upload',str(1)))
            fields.append(('code',''))
            fields.append(('uuid',''))
            fields.extend(ready_tag_ids)
            
            encoder = type(self).create_multipart_encoder(fields=fields)
            
            self.upload_monitor = type(self).create_multipart_monitor(encoder)
    
            initiate = session.post('http://tna.flixupload.com/uploads.php',
                            data=self.upload_monitor,
                            headers={'Content-Type':self.upload_monitor.content_type},
                            proxies=proxy)
            
            self.upload_monitor = type(self).create_multipart_monitor(encoder=encoder,callback=self._hooks['uploading'])                                                

            self.call_hook('uploading',video_upload_request=self.video_upload_request,account=self.account)
            
            tags = tuple([t.name for t in self.video_upload_request.tags])
            description = self.video_upload_request.description.name
            title = self.video_upload_request.title.name
            tag_ids = channel_ids
            video_file = self.video_upload_request.video_file
            
            uploader = UbrUploader(domain='tna.flixupload.com',
                                    path_to_ubr='/',
                                    http_settings=self.account.http_settings,
                                    callback=self._hooks['uploading'])
            

    
            upload_id = uploader.upload(video_file,title,tags,description,tag_ids)
            
            url = 'http://tna.flixupload.com/uploads.php?upload_id={id}'.format(id=upload_id)
            finish = session.get(url,proxies=proxy)

        except Exception as exc:
            self.call_hook('failed',video_upload_request=self.video_upload_request,
                                    account=self.account,
                                    traceback=traceback.format_exc(),
                                    exc_info=sys.exc_info())

            print traceback.format_exc()
            if self.bubble_up_exception:
                raise exc
        
        else:
            self.call_hook('finished',
                            video_request=self.video_upload_request,
                            account=self.account,
                            settings={'video_id':upload_id})
            
            return {'video_id':upload_id}

 


    

    
