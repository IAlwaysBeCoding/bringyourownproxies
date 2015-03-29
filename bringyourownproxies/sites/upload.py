#!/usr/bin/python
import re
import os

import requests
import arrow
import path

from lxml import etree
from lxml.etree import HTMLParser,tostring

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.sites.tnaflix.account import TnaflixAccount

class UbrException(Exception):
    pass

class UbrUploader(object):
    
    def __init__(self,domain,**kwargs):
        
        self.domain = domain
        self.http_settings = kwargs.get('http_settings',HttpSettings())
        self.path_to_cgi = kwargs.get('path_to_cgi','/cgi-bin/')
        self.path_to_ubr = kwargs.get('path_to_ubr','/')
        
    
    def _get_path_to_ubr(self):
        if self.domain.startswith('http://') or self.domain.startswith('https://'):
            return '{domain}{path_to_ubr}'.format(domain=self.domain,path_to_ubr=self.path_to_ubr)
        else:
            return 'http://{domain}{path_to_ubr}'.format(domain=self.domain,path_to_ubr=self.path_to_ubr)

    def _get_path_to_cgi(self):

        if self.domain.startswith('http://') or self.domain.startswith('https://'):
            return '{domain}{path_to_cgi}'.format(domain=self.domain,path_to_cgi=self.path_to_cgi)
        else:
            return 'http://{domain}{path_to_cgi}'.format(domain=self.domain,path_to_cgi=self.path_to_cgi)

        
    def _initiate_new_upload(self,session=None,proxy=None):
        """returns a new upload id request that is assigned to a video request
            used through out the entire uploading processs 
        """
        
        session = session or self.http_settings.session
        proxy = proxy or self.http_settings.proxy
        
        main_url = self._get_path_to_ubr()
        
        now = arrow.utcnow().timestamp
        later = arrow.utcnow().timestamp
        q = "rnd_id={rnd_id}&_{_}={_}".format(rnd_id=now,_=later)
        url = '{main_url}ubr_link_upload.php?{q}'.format(main_url=main_url,q=q)
        get_id_page = session.get(url,proxies=proxy)
        regex = r'startUpload\("(.*?)",0\)'
        is_ready = re.findall(regex,get_id_page.content,re.I|re.M)
        
        if is_ready:
            return is_ready[0]
        else:
            raise UbrException('Cannot retrieve Ubr id from {url}'.format(url=url)) 

    def _start_progress_tracker(self,upload_id,session=None,proxy=None):

        session = session or self.http_settings.session
        proxy = proxy or self.http_settings.proxy
        
        main_url = self._get_path_to_ubr()
        now = arrow.utcnow().timestamp
        q = "upload_id={upload_id}&_={_}".format(upload_id=upload_id,_=now)
        url = '{main_url}ubr_set_progress.php?{q}'.format(main_url=main_url,q=q)
        set_progress_page = session.get(url,proxies=proxy)
        
    def upload(self,video_file,title,tags,description,
                    tag_ids,upload_id=None,upload_monitor=None,
                    session=None,proxy=None):
        
        if isinstance(tag_ids,(list,tuple)):
            tag_ids = [("listch",str(t)) for t in tag_ids]
        else:
            tag_ids = [("listch",str(tag_ids))]
            
        upload_id = upload_id or self._initiate_new_upload()

        session = session or self.http_settings.session
        proxy = proxy or self.http_settings.proxy
        
        main_url = self._get_path_to_cgi()
        now = arrow.utcnow().timestamp
        q = "upload_id={upload_id}".format(upload_id=upload_id)
        url = "{main_url}ubr_upload.pl?{q}".format(main_url=main_url,q=q)

        fields = []
        if not upload_monitor:
            fields.append(('MAX_FILE_SIZE', str(os.path.getsize(video_file))))
            fields.append(('upload_range', str(1)))
            fields.append(('adult', ''))
            fields.append(('field_myvideo_keywords', " ".join([t for t in tags])))
            fields.append(('field_myvideo_title', title))
            fields.append(('field_myvideo_descr', description))
            fields.append(('upfile_0',(path.Path(video_file).name,open(video_file, 'rb'))))
            fields.extend(tag_ids)
            
            multipart_encoder = MultipartEncoder(fields)
            monitor = MultipartEncoderMonitor(multipart_encoder)

        upload = session.post(url,data=monitor,headers={'Content-Type':monitor.content_type},proxies=proxy)
        self._start_progress_tracker(upload_id=upload_id)

        return upload_id    

if __name__ == '__main__':
    
    account =  TnaflixAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    http_settings = account.http_settings
    session = http_settings.session 
    proxy = http_settings.proxy
    
    go_to_upload = session.get('https://www.tnaflix.com/upload.php',proxies=proxy)

    fields = []
    
    tags =("sexy","teen","ass","anal","amateur")
    description = "Sexy Girl getting fucked"
    title = "Sexy Girl"
    tag_ids = [6,4]
    video_file = '/home/ubuntu/workspace/testfiles/test_video.mp4'
    
    ready_tag_ids = [('chlist[]',str(t)) for t in tag_ids]
    fields.append(('field_myvideo_title',title))
    fields.append(('field_myvideo_descr',description))
    fields.append(('field_myvideo_keywords'," ".join([t for t in tags])))
    fields.append(('declared','on'))
    fields.append(('action_upload',str(1)))
    fields.append(('code',''))
    fields.append(('uuid',''))
    fields.extend(ready_tag_ids)
    print fields
    e = MultipartEncoder(fields)
    m = MultipartEncoderMonitor(e)
    
    initiate = session.post('http://tna.flixupload.com/uploads.php',
                            data=m,
                            headers={'Content-Type':'multipart/form-data',
                                    'Origin':'http://tna.flixupload.com',
                                    'Referer':'http://tna.flixupload.com/uploads.php?PHPSESSID=3d45g76lr18vg1pjvd0rqlps55'},
                            proxies=proxy)

    with open('initiate.html','w+') as f:
        f.write(initiate.content)


    uploader = UbrUploader(domain='tna.flixupload.com',
                            path_to_ubr='/',
                            http_settings=http_settings)
    

    
    upload_id = uploader.upload(video_file,title,tags,description,tag_ids)
    
    session = account.http_settings.session
    proxy = account.http_settings.proxy
    url = 'http://tna.flixupload.com/uploads.php?upload_id={id}'.format(id=upload_id)
    finish = session.get(url,proxies=proxy)
    print finish.url
    with open('save.html','w+') as f:
        f.write(finish.content)
    print finish.content 