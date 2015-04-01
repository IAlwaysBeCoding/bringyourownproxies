#!/usr/bin/python

import os
import json
import re
import sys
import traceback

import path
from requests_toolbelt import MultipartEncoder
from werkzeug.datastructures import MultiDict
from lxml import etree
from lxml.etree import HTMLParser,tostring
from bringyourownproxies.errors import (InvalidVideoUploadRequest,InvalidVideoUrl,InvalidAccount,
                                        NotLogined,FailedUpload,FailedUpdatingVideoSettings)

from bringyourownproxies.sites.upload import _Upload

from bringyourownproxies.sites.sex.account import SexAccount
from bringyourownproxies.sites.sex.video import SexVideoPinRequest


class SexUploadVideo(_Upload):
    
    def start(self,**kwargs):

        try:
            if type(self.video_upload_request) != SexVideoPinRequest:
                raise InvalidVideoUploadRequest('Invalid pin_video_request, '\
                                                'it needs to be a SexVideoPinRequest instance')
                                                
            if type(self.account) != SexAccount:
                raise InvalidVideoUploadRequest('Invalid account, '\
                                                'it needs to be a SexAccount instance')
            if not self.account.is_logined():
                raise NotLogined('Sex account is not logined')
    
            session = self.account.http_settings.session
            proxy = self.account.http_settings.proxy
            
            self.call_hook('started',video_upload_request=self.video_upload_request,account=self.account)
            video_upload = session.get('http://upload.sex.com/video/add',proxies=proxy)
            
            find_sess_sex = re.findall(r"{'sess_sex' : '(.*?)'",video_upload.content,re.I|re.M)
            if not find_sess_sex:
                raise FailedUpload('Could not find sess_sex, its needed to upload')
            
            sess_sex = find_sess_sex[0]
            video_file = self.video_upload_request.video_file
            
            video_data = type(self).create_multipart_encoder(fields={'Filename':path.Path(video_file).name,
                                                                    'sess_sex': sess_sex,
                                                                    'Upload':'Submit Query',
                                                                    'Filedata': (path.Path(video_file).name,open(video_file, 'rb'))})
            
            self.upload_monitor = type(self).create_multipart_monitor(encoder=video_data,callback=self._hooks['uploading'])

            attempt_upload=session.post('http://upload.sex.com/video/upload',
                                        data=self.upload_monitor,
                                        proxies=proxy,
                                        headers={'Content-Type': self.upload_monitor.content_type,"Connection":"Keep-Alive"})
            
    
            if attempt_upload.content == 'Error: You cannot upload more than 5 videos per hour':
                raise FailedUpload('Reach uploading limit')
            
    
            is_uploaded = self._update_temporary_video_pin(tmp_video=attempt_upload.content)
            
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
            
            if is_uploaded:
                return {'video_id':is_uploaded}
            else:
                return False


    def _update_temporary_video_pin(self,tmp_video):
        if not self.account.is_logined():
            raise NotLogined('Sex account is not logined')
            
        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy
        
        url = 'http://upload.sex.com/pin/create?video=1&tmpFile={tmp}&from=upload'.format(tmp=tmp_video)
        create_video = session.get(url,proxies=proxy)
        url = 'http://www.sex.com/pin/create?video=1&tmpFile={tmp}&from=upload'.format(tmp=tmp_video)
        
    
        post = {"custom_tags":",".join([t.name.lower() for t in self.video_upload_request.sex_tags]),
                "board":self.video_upload_request.board.board_id,
                "board_name":self.video_upload_request.board.name,
                "title":str(self.video_upload_request.title),
                "submit":"Pin It"}
             
    
        set_settings = session.post(url,data=post,proxies=proxy)
    
        if 'Congratulations! Your pin has been added.' in set_settings.content:
            doc = etree.fromstring(set_settings.content,HTMLParser())
            get_video_id = doc.xpath('//a[@target="_blank"]')[0].attrib['href'].replace('http://www.sex.com/pin/','').replace('/','')
            return int(get_video_id)
        else:
            raise FailedUpload('Unknown problem, failed pinning video')
    
    @staticmethod
    def change_video_pin_settings(video_id,settings,account):
        
        session = account.http_settings.session
        proxy = account.http_settings.proxy
    
        if not account.is_logined():
            raise NotLogined('Sex account is not logined')
    
        url = 'http://www.sex.com/pin/edit/{video_id}'.format(video_id=video_id)
    
        post = {'board_id':settings['board_id'],
                'custom_tags':",".join([t for t in settings['tags']]),
                'title':settings['title'],
                'submit':'Save Changes'}
                
        change_pin = session.post(url,data=post,proxies=proxy)
        doc = etree.fromstring(change_pin.content,HTMLParser())
        if doc.xpath('//h2'):
            if doc.xpath('//h2')[0].text == "The page you're looking for could not be found.":
                raise InvalidVideoUrl('Invalid video id, it could not be found on sex.com')
    
        return True

