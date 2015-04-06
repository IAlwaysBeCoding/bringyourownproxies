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
from bringyourownproxies.upload import Upload

from bringyourownproxies.sites.errors import KummProblem


class _Upload(Upload):
    
    def __init__(self,account,video_upload_request,**kwargs):
        
        self.account = account
        self.video_upload_request = video_upload_request
        
        super(_Upload,self).__init__(**kwargs)
    

class MultipleDomainUploader(object):
    
    def __init__(self,domain):
        self.domain = domain 
    
    def _join_part_to_domain(self,part):
        if self.domain.startswith('http://') or self.domain.startswith('https://'):
            return '{domain}{part}'.format(domain=self.domain,path=part)
        else:
            return 'http://{domain}{path}'.format(domain=self.domain,path=part)

    
class UbrException(Exception):
    pass

class UbrUploader(MultipleDomainUploader):
    
    def __init__(self,domain,**kwargs):
        
        self.domain = domain
        self.http_settings = kwargs.get('http_settings',HttpSettings())
        self.path_to_cgi = kwargs.get('path_to_cgi','/cgi-bin/')
        self.path_to_ubr = kwargs.get('path_to_ubr','/')
        
    
    def _get_path_to_ubr(self):
        return self._join_part_to_domain(part=self.path_to_ubr)

    def _get_path_to_cgi(self):
        return self._join_part_to_domain(part=self.path_to_cgi)

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
        
    def upload(self,video_file,title,tags,description,tag_ids,upload_id=None,callback=None,session=None,proxy=None):
        
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
        fields.append(('MAX_FILE_SIZE', str(os.path.getsize(video_file))))
        fields.append(('upload_range', str(1)))
        fields.append(('adult', ''))
        fields.append(('field_myvideo_keywords', " ".join([t for t in tags])))
        fields.append(('field_myvideo_title', title))
        fields.append(('field_myvideo_descr', description))
        fields.append(('upfile_0',(path.Path(video_file).name,open(video_file, 'rb'))))
        fields.extend(tag_ids)
        
        multipart_encoder = MultipartEncoder(fields)

        if callback:
            monitor = MultipartEncoderMonitor(multipart_encoder,callback)
        else:
            monitor = MultipartEncoderMonitor(multipart_encoder)
            
        upload = session.post(url,data=monitor,headers={'Content-Type':monitor.content_type},proxies=proxy)
        self._start_progress_tracker(upload_id=upload_id)

        return upload_id    


class KummUploader(MultipleDomainUploader):
    
    def __init__(self,domain,website,username,**kwargs):
        
        self.domain = domain
        self.website = website
        self.username = username
        self.http_settings = kwargs.get('http_settings',HttpSettings())
        self.path_to_api = kwargs.get('path_to_api','/api/')
        
    def _get_path_to_upload(self):
        
        path = '/users/{user}/videos'.format(user=self.username)
        return self._join_part_to_domain(part=path)
    
    def upload(self,video_file,title,pornstars,tags,orientation,callback=None,session=None,proxy=None):
        
        session = session or self.http_settings.session
        proxy = proxy or self.http_settings.proxy
        
        upload_path = self._get_path_to_upload()
        go_to_upload = session.get(upload_path,proxies=proxy)
        
        upload_form_url = self._join_part_to_domain(part='/users/video/upload')
        session.headers.update({'X-Requested-With':'XMLHttpRequest'})
        get_upload_form = session.get(upload_form_url,proxies=proxy)
        
        regex_api_key = r'var kumm_api_key                    = "(.*?)"'
        regex_user_id = r'var user_id                    = "(.*?)"'
        regex_callback_url = r'var callback_url                    = "(.*?)"'
        
        found_api_key = re.search(regex_api,get_upload_form.content)
        found_user_id = re.search(regex_user_id,get_upload_form.content)
        found_callback_url = re.search(regex_callback_url,get_upload_form.content)
        
        if not found_api_key:
            raise KummProblem('Could not find api_key')
        if not found_user_id:
            raise KummProblem('Could not find user_id')
        if not found_callback_url:
            raise KummProblem('Could not find callback_url')

        api_key = found_api_key.group(1)
        user_id = found_user_id.group(1)
        callback_url = found_callback_url.group(1)

        doc = etree.fromstring(get_upload_form.content,HTMLParser())
        get_upload_url = doc.xpath('//input[@id="fileupload"]/@dataurl')            
        
        if len(get_upload_url) == 0:
            raise KummProblem('Could not find kumm posting url for the video upload')
        
        posting_url = get_upload_url[0]    
        session.options(posting_url,proxies=proxy)
        
        fields = []
        fields.append(('token',api_key))
        fields.append(('callBackUrl',callback_url))
        fields.append(('website',self.website))
        fields.append(('user_id',user_id))
        fields.append(('files[]',(path.Path(video_file).name,open(video_file, 'rb'))))

        encoder = MultipartEncoder(fields)
        if callback:
            monitor = MultipartEncoderMonitor(encoder,callback)
        else:
            monitor = MultipartEncoderMonitor(encoder)
            
        submit_upload = session.post(posting_url,
                                    data=monitor,
                                    headers={'Content-Type':monitor.content_type},                                    
                                    proxies=proxy)

        with open('submit_upload.html','w+') as f:
            f.write(submit_upload.content)
        

if __name__ == '__main__':
    video_file = '/root/Dropbox/shower.mp4'
    title = 'Hot girl taking a shower'
    pornstars = ''
    tags = ('girl','shower','amateur')
    orientation = 'Straight'
    
    uploader = KummUploader(domain="http://4tube.com",website="4tube",username="tedwantsmore")
    uploader.upload(video_file,title,pornstars,tags,orientation)
    







