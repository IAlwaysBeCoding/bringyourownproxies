#!/usr/bin/python
import os
import json

import path
from requests_toolbelt import MultipartEncoder
from lxml import etree
from lxml.etree import HTMLParser,tostring
from bringyourownproxies.errors import (InvalidVideoUploadRequest,InvalidAccount,
                                        NotLogined,FailedUpload,FailedUpdatingVideoSettings)
from bringyourownproxies.upload import ON_SUCCESS_UPLOAD,ON_FAILED_UPLOAD

from errors import VideoNotReadyForThumbnail,FailedChangingThumbnailId
from account import YouPornAccount
from video import YouPornVideoUploadRequest

def upload_video(video_upload_request,account,**kwargs):
    on_success_upload = kwargs.get('on_success_upload',ON_SUCCESS_UPLOAD)
    on_failed_upload = kwargs.get('on_failed_upload',ON_FAILED_UPLOAD)
    prepared_upload = kwargs.get('prepare_upload',False)
    try:
        if type(video_upload_request) != YouPornVideoUploadRequest:
            raise InvalidVideoUploadRequest('Invalid video_upload_request, ' \
                                    'it needs to be a YouPornVideoUploadRequest instance')
                                    
        if type(account) != YouPornAccount:
            raise InvalidAccount('Invalid account, it needs to be a YouPornAccount instance')
        
        if not account.is_logined():
            raise NotLogined('YouPorn account is not logined')
            
        if prepared_upload:
            upload_requested = prepared_upload()
        else:
            upload_requested = prepare_upload(video_upload_request,account)
        
        user_uploader_id = upload_requested['user_uploader_id']
        video_id = upload_requested['video_id']
        session = account.http_settings.session
        proxy = account.http_settings.proxy
        session.headers.update({"X-Requested-With":"XMLHttpRequest"})
        video_type = video_upload_request.video_file.split('.')[-1]

        video_file = video_upload_request.video_file
        video_data = MultipartEncoder(fields={'userId':str(user_uploader_id),
                                            'videoId': str(video_id),
                                            'files[]': (path.Path(video_file).name,open(video_file, 'rb'))})
        
        attempt_upload = session.post('http://www.youporn.com/upload', data=video_data,
        proxies=proxy,headers={'Content-Type': video_data.content_type,"Connection":"Keep-Alive"})
        
        del session.headers['X-Requested-With']

        update_video_settings(video_upload_request,video_id,account)
    except Exception as exc:
        on_failed_upload(exc=exc,video_request=video_upload_request,account=account)
        raise exc
    else:
        on_success_upload(video_request=video_upload_request,
                        account=account,
                        settings={'video_id':upload_requested['video_id']})
        return {'video_id':upload_requested['video_id']}

def prepare_upload(video_request,account):
    session = account.http_settings.session
    proxy = account.http_settings.proxy
    
    if not account.is_logined():
        raise NotLogined('YouPorn account is not logined')
    
    session.get('http://www.youporn.com/upload',proxies=proxy)
    session.headers.update({"X-Requested-With":"XMLHttpRequest",
                            "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"})
                            
    video_size = os.path.getsize(video_request.video_file)
    video = path.Path(video_request.video_file)
    post = {'file':video.name,'size':video_size}

    create_upload_request = session.post('http://www.youporn.com/upload/create-videos/',data=post,proxies=proxy)
    
    response = json.loads(create_upload_request.content)
    if 'success' in response:
        if not response['success']:
            raise FailedUpload('Failed to upload video reason:{reason}'.format(reason=response['reason']))
    
    del session.headers['X-Requested-With']
    return response

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

def pick_thumb_nail(video_id,account,thumbnail_id=1):
    session = account.http_settings.session
    proxy = account.http_settings.proxy
    
    if not account.is_logined():
        raise NotLogined('YouPorn account is not logined')
    
    url = 'http://www.youporn.com/change/video-thumbnail/' \
        '{videoId}/{thumbnailId}/'.format(videoId=video_id,thumbnailId=thumbnail_id)
    
    update_thumbnail = session.post(url,proxies=proxy)
    
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


if __name__ == '__main__':

    from bringyourownproxies.video import Description,Title
    from video import YouPornTag,YouPornCategory
    import functools
    
    account = YouPornAccount(email="tedwantsmore@gmx.com",username="tedwantsmore",password="money1003")
    video_file = '/home/ubuntu/workspace/bringyourownproxies/testfiles/daughter.mp4'
    title = Title("Daughter ")
    tags = (YouPornTag("Amateur"),YouPornTag("Ass"),YouPornTag("Anal"),YouPornTag("Daughter"))
    category = YouPornCategory('Amateur')
    description = Description("Daughter getting fucked by dad really hard")
    print type(description)
    print type(category)
    video_request = YouPornVideoUploadRequest(video_file=video_file,
                                            title=title,
                                            tags=tags,
                                            category=category,
                                            description=description)
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
    upload_video = upload_video(on_success_upload=success_callback,on_failed_upload=failed_callback)
    
    print pick_thumb_nail(11016857,account,12)
    
    #uploader.upload(video_request=video_request,account=account)
    