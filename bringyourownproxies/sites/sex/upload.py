#!/usr/bin/python

import os
import json
import re 

import path
from requests_toolbelt import MultipartEncoder
from werkzeug.datastructures import MultiDict
from lxml import etree
from lxml.etree import HTMLParser,tostring
from bringyourownproxies.errors import (InvalidVideoUploadRequest,InvalidVideoUrl,InvalidAccount,
                                        NotLogined,FailedUpload,FailedUpdatingVideoSettings)

from bringyourownproxies.upload import Upload

from bringyourownproxies.sites.sex.account import SexAccount
from bringyourownproxies.sites.sex.video import SexVideoPinRequest



def pin_video(pin_video_request,account,**kwargs):
    on_success_upload = kwargs.get('on_success_upload',ON_SUCCESS_UPLOAD)
    on_failed_upload = kwargs.get('on_failed_upload',ON_FAILED_UPLOAD)

    try:
        if type(pin_video_request) != SexVideoPinRequest:
            raise InvalidVideoUploadRequest('Invalid pin_video_request, '\
                                            'it needs to be a SexVideoPinRequest instance')
                                            
        if type(account) != SexAccount:
            raise InvalidVideoUploadRequest('Invalid pin_video_request, '\
                                            'it needs to be a SexVideoPinRequest instance')
        if not account.is_logined():
            raise NotLogined('Sex account is not logined')


        session = account.http_settings.session
        proxy = account.http_settings.proxy
        
        video_upload = session.get('http://upload.sex.com/video/add',proxies=proxy)
        find_sess_sex = re.findall(r"{'sess_sex' : '(.*?)'",video_upload.content,re.I|re.M)
        if not find_sess_sex:
            raise FailedUpload('Could not find sess_sex, its needed to upload')
        sess_sex = find_sess_sex[0]
        
        
        video_data = MultipartEncoder(fields={'Filename':path.Path(video_file).name,
                                            'sess_sex': sess_sex,
                                            'Upload':'Submit Query',
                                            'Filedata': (path.Path(video_file).name,open(video_file, 'rb'))})
        
        attempt_upload = session.post('http://upload.sex.com/video/upload', data=video_data,
        proxies=proxy,headers={'Content-Type': video_data.content_type,"Connection":"Keep-Alive"})
        

        if attempt_upload.content == 'Error: You cannot upload more than 5 videos per hour':
            raise FailedUpload('Reach uploading limit')
        

        is_uploaded = update_temporary_video_settings(tmp_video=attempt_upload.content,
                                                            video_request=video_request,
                                                            account=account)
        
        if is_uploaded:
            return is_uploaded
        else:
            return False

    except InvalidAccount as exc:
        on_failed_upload(exc=exc,video_request=pin_video_request,account=account)
        raise exc
    else:
        on_success_upload(video_request=pin_video_request,account=account)
        
def update_temporary_video_settings(tmp_video,video_request,account):
           
    if not account.is_logined():
        raise NotLogined('Sex account is not logined')
    session = account.http_settings.session
    proxy = account.http_settings.proxy
    
    url = 'http://upload.sex.com/pin/create?video=1&tmpFile={tmp}&from=upload'.format(tmp=tmp_video)
    create_video = session.get(url,proxies=proxy)
    url = 'http://www.sex.com/pin/create?video=1&tmpFile={tmp}&from=upload'.format(tmp=tmp_video)
    

    post = {"custom_tags":",".join([t.name.lower() for t in video_request.sex_tags]),
            "board":video_request.board.board_id,
            "board_name":video_request.board.name,
            "title":str(video_request.title),
            "submit":"Pin It"}
         

    set_settings = session.post(url,data=post,proxies=proxy)

    if 'Congratulations! Your pin has been added.' in set_settings.content:
        doc = etree.fromstring(set_settings.content,HTMLParser())
        get_video_id = doc.xpath('//a[@target="_blank"]')[0].attrib['href'].replace('http://www.sex.com/pin/','').replace('/','')
        return int(get_video_id)
    else:
        raise FailedUpload('Unknown problem, failed pinning video')
   
def update_video_settings(video_id,settings,account):
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

class SexPinVideo(Upload):
    
    def __init__(self,account,video_upload_request,**kwargs):
        
        self.account = account
        self.video_upload_request = video_upload_request
        
        hooks = kwargs.get('hooks',{})
        bubble_up_exception = kwargs.get('bubble_up_exception',False)
        super(YouPornUpload,self).__init__(hooks=hooks,bubble_up_exception=bubble_up_exception)

    def start(self,**kwargs):
        on_success_upload = kwargs.get('on_success_upload',ON_SUCCESS_UPLOAD)
        on_failed_upload = kwargs.get('on_failed_upload',ON_FAILED_UPLOAD)
    
        try:
            if type(pin_video_request) != SexVideoPinRequest:
                raise InvalidVideoUploadRequest('Invalid pin_video_request, '\
                                                'it needs to be a SexVideoPinRequest instance')
                                                
            if type(account) != SexAccount:
                raise InvalidVideoUploadRequest('Invalid pin_video_request, '\
                                                'it needs to be a SexVideoPinRequest instance')
            if not account.is_logined():
                raise NotLogined('Sex account is not logined')
    
    
            session = account.http_settings.session
            proxy = account.http_settings.proxy
            
            video_upload = session.get('http://upload.sex.com/video/add',proxies=proxy)
            find_sess_sex = re.findall(r"{'sess_sex' : '(.*?)'",video_upload.content,re.I|re.M)
            if not find_sess_sex:
                raise FailedUpload('Could not find sess_sex, its needed to upload')
            sess_sex = find_sess_sex[0]
            
            
            video_data = MultipartEncoder(fields={'Filename':path.Path(video_file).name,
                                                'sess_sex': sess_sex,
                                                'Upload':'Submit Query',
                                                'Filedata': (path.Path(video_file).name,open(video_file, 'rb'))})
            
            attempt_upload = session.post('http://upload.sex.com/video/upload', data=video_data,
            proxies=proxy,headers={'Content-Type': video_data.content_type,"Connection":"Keep-Alive"})
            
    
            if attempt_upload.content == 'Error: You cannot upload more than 5 videos per hour':
                raise FailedUpload('Reach uploading limit')
            
    
            is_uploaded = update_temporary_video_settings(tmp_video=attempt_upload.content,
                                                                video_request=video_request,
                                                                account=account)
            
            if is_uploaded:
                return is_uploaded
            else:
                return False

        except InvalidAccount as exc:
            on_failed_upload(exc=exc,video_request=pin_video_request,account=account)
            raise exc
        else:
            on_success_upload(video_request=pin_video_request,account=account)
    def _update_temporary_video_pin(self,tmp_video):
        if not self.account.is_logined():
            raise NotLogined('Sex account is not logined')
            
        session = self.account.http_settings.session
        proxy = self.account.http_settings.proxy
        
        url = 'http://upload.sex.com/pin/create?video=1&tmpFile={tmp}&from=upload'.format(tmp=tmp_video)
        create_video = session.get(url,proxies=proxy)
        url = 'http://www.sex.com/pin/create?video=1&tmpFile={tmp}&from=upload'.format(tmp=tmp_video)
        
    
        post = {"custom_tags":",".join([t.name.lower() for t in self.video_request.sex_tags]),
                "board":self.video_request.board.board_id,
                "board_name":self.video_request.board.name,
                "title":str(self.video_request.title),
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

if __name__ == '__main__':
    
    from bringyourownproxies.video import Description,Title
    from video import SexTag
    from board import SexBoard
    import functools
    
    account = SexAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    video_file = '/home/ubuntu/workspace/bringyourownproxies/testfiles/test_video.mp4'
    title = Title("Sobe with lukas and Ken with jr on the bottom")
    board = SexBoard('girls',696286)
    tags = (SexTag("Amateur"),SexTag("Ass"),)
    sex_tags = (SexTag('Teen'),)
    video_request = SexVideoPinRequest(video_file=video_file,
                                        title=title,
                                        tags=tags,
                                        board=board,
                                        sex_tags=sex_tags)
    print video_request
    #print video_request.create_video_settings()
    account.login()
    def success(video_request,account):
        print 'success'
        print video_request
        print account
    def failed(exc,video_request,account):
        print 'failed'
        print exc
        print video_request
        print account    
    success_callback = functools.partial(success)
    failed_callback = functools.partial(failed)
    uploader = pin_video(on_success_upload=success_callback,on_failed_upload=failed_callback)
    #print uploader.pin_video(pin_video_request=video_request,account=account)

    settings = {'board_id':696286,
                'tags':['daddy','girls','white','squirt','anal'],
                'title':'sex isnt that good'}
    update_video_settings(27234868,settings,account)
