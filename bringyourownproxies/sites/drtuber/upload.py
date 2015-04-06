#!/usr/bin/python
import os
import re
import json
import sys
import traceback
import time 

import path

from requests.cookies import create_cookie
from requests_toolbelt import MultipartEncoder
from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.errors import (InvalidVideoUploadRequest,InvalidAccount,NotLogined,
                                        InvalidTitle,InvalidThumbnailId,FailedUpload)
from bringyourownproxies.sites.upload import _Upload
from bringyourownproxies.sites.drtuber.errors import CannotFindSid
from bringyourownproxies.sites.drtuber.account import DrTuberAccount
from bringyourownproxies.sites.drtuber.video import DrTuberVideoUploadRequest

__all__ = ['DrTuberUpload']

class DrTuberUpload(_Upload):

    def start(self):

        try:
            if not isinstance(self.video_upload_request,DrTuberVideoUploadRequest):
                raise InvalidVideoUploadRequest('Invalid video_upload_request, ' \
                                        'it needs to be a DrTuberVideoUploadRequest instance')
                                        
            if not isinstance(self.account,DrTuberAccount):
                raise InvalidAccount('Invalid account, it needs to be a DrTuberAccount instance')
            
            
            if not self.account.is_logined():
                raise NotLogined('DrTuber account is not logined')

            session = self.account.http_settings.session
            proxy = self.account.http_settings.proxy

            go_to_upload = session.get('http://www.drtuber.com/upload/video',proxies=proxy)    
            
            self.call_hook('started',video_upload_request=self.video_upload_request,account=self.account)
            
            session.headers.update({'X-Requested-With':'XMLHttpRequest',
                                    'Origin':'http://www.drtuber.com',
                                    'Referer':'http://www.drtuber.com/upload/video'})


            sid = self._get_avs_value(html=go_to_upload.content)
            tmp_filename = self._upload_video(video_file=self.video_upload_request.video_file,sid=sid)
            
            title = self.video_upload_request.title
            categories = self.video_upload_request.category
            site_link = self.video_upload_request.site_link
            site_name = self.video_upload_request.site_name
            is_private = self.video_upload_request.is_private
            filename = path.Path(self.video_upload_request.video_file).name
            response = self._check_video_commit(commit=tmp_filename)
            self._check_title(title=self.video_upload_request.title)
            
            self._submit_upload(title=title,site_link=site_link,site_name=site_name,
                                is_private=is_private,categories=categories,
                                tmp_filename=tmp_filename,filename=filename)
            
            
            response = self._check_video_commit(commit=tmp_filename)
            
            found_thumbnails = False
            thumbnail_id = self.video_upload_request.thumbnail_id
            
            total_loops = 10
            current_loop = 0
            while not found_thumbnails:
                status = response["status"]
                
                if status == "6":
                    if "thumbs" in response:
                        if len(response["thumbs"]) + 1 > int(thumbnail_id):
                            raise InvalidThumbnailId('Invalid thumbnail_id is not in the thumbnail range')
                        
                        self._set_video_thumbnail(filename=filename,thumbnail_id=int(int(thumbnail_id)-1))
                        found_thumbnails = True
                
                else:
                    current_loop += 1
                    if current_loop == total_loops:
                        raise FailedUpload('{loops} loops went by and no status 6 was found'.format(loops=total_loops))
                    if not found_thumbnails:
                        time.sleep(5)

                
        except Exception as exc:
            del session.headers['X-Requested-With']    
            del session.headers['Origin']
            del session.headers['Referer']
            
            self.call_hook('failed',video_upload_request=self.video_upload_request,
                                    account=self.account,
                                    traceback=traceback.format_exc(),
                                    exc_info=sys.exc_info())

    
            if self.bubble_up_exception:
                raise exc
        
        else:
            del session.headers['X-Requested-With']    
            del session.headers['Origin']
            del session.headers['Referer']
            
            self.call_hook('finished',
                            video_request=self.video_upload_request,
                            account=self.account,
                            settings={'tmp_filename':tmp_filename,
                                        'video_id':None})
            
            return {'video_id':None,'tmp_filename':tmp_filename}

    def _get_avs_value(self,html):
        find_sid = re.search('sid: "(.*?)",',html)
        if find_sid:
            return find_sid.group(1)
        else:
            raise CannotFindSid('Cannot find sid , value needed for AVS')
        
    def _upload_video(self,video_file,sid):
        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy
        
        fields =  []
        fields.append(('name',path.Path(video_file).name))
        fields.append(('AVS',sid))
        fields.append(('action','uploadVideo'))
        fields.append(('Filedata',(path.Path(video_file).name,open(video_file, 'rb'))))
        
        encoder = type(self).create_multipart_encoder(fields=fields)
        
        self.upload_monitor = type(self).create_multipart_monitor(encoder,self._hooks['uploading'])
    
        upload_temporary_file = session.post('http://www.drtuber.com/uploader.php?upload_redirect=1',
                                            data=self.upload_monitor,
                                            headers={'Content-Type':self.upload_monitor.content_type},
                                            proxies=proxy)
        try:
            response = upload_temporary_file.json()
        except:
            raise FailedUpload('Dr tuber failed to upload because of :{msg}'.format(msg=upload_temporary_file.content))
        else:
            if not response['success']:
                raise FailedUpload('Dr tuber error:{r}'.format(r=response['error']))

            return response['upload_data']['tmp_filename']

    def _submit_upload(self,title,site_link,site_name,is_private,categories,tmp_filename,filename):
        
        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy
        
        post = [('title',title),
                ('site_link',site_link if site_link else ""),
                ('site_name',site_name if site_name else ""),
                ('terms','true'),
                ('private',"1" if is_private else "0"),
                ('track','null'),
                ('tmp_filename',tmp_filename),
                ('filename',filename),
                ('action','commitVideo'),
                ('upload_redirect',1)]

        if isinstance(categories,(list,tuple)):
            for category in categories:
                post.append(('categories[]',str(category.category_id)))
        else:
            post.append(('categories[]',str(categories.category_id)))
        
        submit_video = session.post('http://www.drtuber.com/uploader.php?upload_redirect=1',data=post,proxies=proxy)
        
    def _check_title(self,title):
        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy
        
        session.headers.update({"X-Requested-With":"XMLHttpRequest"})
        post = {'action':'checkTitle','title':title}
        check_title = session.post('http://www.drtuber.com/uploader.php?upload_redirect=1',data=post,proxies=proxy)
        response = check_title.json()
        if response['success']:
            return True
        else:
            raise InvalidTitle('Not a valid title for DrTuber acceptance'\
                                ' errors:{errors}'.format(errors=response['error']))

    def _check_video_commit(self,commit):
        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy
        
        post = {'action':'checkVideoCommit','file_name':commit}
        check_commit = session.post('http://www.drtuber.com/uploader.php?upload_redirect=1',data=post,proxies=proxy)
        try:
            response = check_commit.json()
        except:
             raise FailedUpload('Dr tuber failed comitting video:{commit} due to :{msg}'.format(commit=commit,
                                                                                                msg=check_commit.content))
        else:
            if not response['success']:
                raise FailedUpload('Dr tuber failed comitting video:{commit} due to :{msg}'.format(commit=commit,
                                                                                                    msg=response['error']))
            return response

    def _get_thumbnail_options(self,commit):
        
        response = self._check_video_commit(commit=commit)
        if response['success']:
            if response['status'] == '6':
                return response['thumbs']
            else:
                raise FailedUpload('Unknown status:{status} when getting thumbnail options '\
                                    ' from commit:{commit} '.format(commit=commit,
                                                                    status=response['status']))
        else:
           raise FailedUpload('Dr tuber failed getting thumbnail options video:{commit} due to :{msg}'.format(commit=commit,
                                                                                                        msg=response['error']))
    
    def _set_video_thumbnail(self,filename,thumbnail_id):
        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy
        
        post = {'action':'setVideoThumb',
                'file_name':filename,
                'thumb':thumbnail_id}
        
        set_thumbnail = session.post('http://www.drtuber.com/uploader.php?upload_redirect=1',data=post,proxies=proxy)
        response = set_thumbnail.json()
        if not response['success']:
            raise InvalidThumbnailId('Dr tuber failed setting thumbnail{thumb}:'\
                                        '{commit} due to :{msg}'.format(commit=commit,
                                                                thumb=thumbnail_id,
                                                                msg=response['error']))
        return response
            
    
    
    

    
