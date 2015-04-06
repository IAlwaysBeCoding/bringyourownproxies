#!/usr/bin/python
import re
import os

import requests
import arrow
import path


from urlobject import URLObject
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

class UbrException(Exception):
    pass

class UbrUploader(object):
    
    def __init__(self,domain,**kwargs):
        
        self.domain = domain
        self.http_settings = kwargs.get('http_settings',HttpSettings())
        self.path_to_cgi = kwargs.get('path_to_cgi','/cgi-bin/')
        self.path_to_ubr = kwargs.get('path_to_ubr','/')
        
    
    def _get_path_to_ubr(self):
        domain = URLObject(self.domain)
        return domain.with_path(self.path_to_ubr)

    def _get_path_to_cgi(self):
        domain = URLObject(self.domain)
        return domain.with_path(self.path_to_cgi)

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

class KummUploader(object):
    
    def __init__(self,domain,website,username,**kwargs):
        
        self.domain = domain
        self.website = website
        self.username = username
        
        self.autocorrect_tags = kwargs.get('autocorrect_tags',False)
        self.add_all_autocorrect_tags = kwargs.get('add_all_autocorrect_tags',False)
        self.drop_incorrect_tags = kwargs.get('drop_incorrect_tags',False)
        
        self.http_settings = kwargs.get('http_settings',HttpSettings())
        self.path_to_api = kwargs.get('path_to_api','/api/')
    
    def _add_www(self,url):
        domain = URLObject(url)
        original_scheme = domain.scheme
        if not domain.hostname.startswith('www'):
            hostname = domain.hostname
            domain_with_www = hostname.replace(domain.hostname,'www.{domain}'.format(domain=domain.hostname))
            domain = URLObject("{scheme}://{domain}".format(scheme=original_scheme,domain=domain_with_www))
        return domain

    def _get_path_to_upload(self,add_www=True):
        if add_www:
            domain = self._add_www(self.domain)
        
        return domain.with_path('/users/{user}/videos'.format(user=self.username))

    def _get_path_to_users_upload(self,add_www=True):
        if add_www:
            domain = self._add_www(self.domain) 

        return domain.with_path('/users/video/upload')
    
    def _get_sexuality_id(self,orientation):
        
        if orientation.lower() == 'straight':
            sexuality = 1
        elif orientation.lower() == 'gay':
            sexuality = 2
        elif orientation.lower() == 'transsexual':
            sexuality = 3
        else:
            raise KummProblem('Invalid orientation. Orientation can only be straight,gay or transsexual')
        
        return sexuality
        
    def _get_correct_tag_url(self,sexuality,tag,add_www=True):
        
        if add_www:
            domain = self._add_www(self.domain)
        
        return domain.\
                    add_path('/autocomplete/tag').\
                    set_query_params([('sexuality',sexuality),('term',tag.lower())])

         
    def _upload_video(self,video_file,callback,session,proxy):
        
        upload_path = self._get_path_to_upload()
        go_to_upload = session.get(upload_path,proxies=proxy)
        
        upload_form_url = self._get_path_to_users_upload()

        session.headers.update({'X-Requested-With':'XMLHttpRequest'})
        get_upload_form = session.get(upload_form_url,proxies=proxy)
        
        regex_api_key = r'var\s+kumm_api_key\s+=\s+"(.*?)"'
        regex_user_id = r'var\s+user_id\s+=\s+"(.*?)"'
        regex_callback_url = r'var\s+callback_url\s+=\s+"(.*?)"'
        
        found_api_key = re.search(regex_api_key,get_upload_form.content)
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
        get_upload_url = doc.xpath('//input[@id="fileupload"]/@data-url')            
                
        if len(get_upload_url) == 0:
            raise KummProblem('Could not find kumm posting url for the video upload')
        
        posting_url = get_upload_url[0]    
        session.options(posting_url,proxies=proxy)
        
        fields = []
        fields.append(('token',api_key))
        fields.append(('callBackUrl',callback_url))
        fields.append(('website',self.website))
        fields.append(('userId',user_id))
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
        try:
            response = submit_upload.json()
        except:
            raise KummProblem('Expecting json, did not receive json after video uploading')
        else:
            if 'err' in response:
                raise KummProblem('Kumm uploader experienced an error after uploading:{err}'.format(err=response['err']))
            elif 'uuid' in response:
                return response['uuid']

    def upload(self,video_file,title,pornstars,tags,orientation,callback=None,session=None,proxy=None):
        
        session = session or self.http_settings.session
        proxy = proxy or self.http_settings.proxy

        uuid = self._upload_video(video_file=video_file,callback=callback,session=session,proxy=proxy)
        if not isinstance(tags,(list,tuple)):
            tags = [tags]
        elif isinstance(tags,tuple):
            tags = list(tags)
        
        sexuality = self._get_sexuality_id(orientation)
        corrected_tags = [( tag,
                            session.get(self._get_correct_tag_url(sexuality,tag),proxies=proxy).json()) 
                            for tag in tags]
        
        for corrected_tag in corrected_tags:
            tag,tags_options = corrected_tag
            if len(tags_options) == 0:
                if not self.autocorrect_tags:
                    raise KummProblem('Tag:{t} is not a valid tag, autocorrect is set to False'.format(t=tag))
                else:
                    if self.drop_incorrect_tags:
                        del tags[tags.index(tag)]
                    
                    if self.add_all_autocorrect_tags:
                        tags.extend([t['label'] for t in tags_options])
            else:
                if self.add_all_autocorrect_tags:
                    tags.extend([t['label'] for t in tags_options])
        

        post = {'sexuality':str(sexuality),
                'title':title,
                'pornstars':pornstars if pornstars else "",
                'tags':",".join([tag.lower() for tag in tags]),
                'terms':'on',
                'fileName':'',
                'mimeType':'',
                'size':'',
                'uuid':uuid}
        
        submit_url = self._get_path_to_users_upload()
        submit_video = session.post(submit_url,data=post,proxies=proxy)
        try:
            response = submit_video.json()
        except:
            raise KummProblem('Expecting json, did not receive json after submited video')
        else:
            if 'status' in response:
                if response['status'] == 'ok':
                    return True
                else:
                    raise KummProblem('Unknown status:{status}'.format(status=response['status']))

if __name__ == '__main__':
    from bringyourownproxies.sites import _4tubeAccount
    account = _4tubeAccount(username="tedwantsmore",password="money1003",email="tedwantsmore@gmx.com")
    account.login()
    
    video_file = '/root/Dropbox/shower.mp4'
    title = 'Hot girl taking a shower'
    pornstars = None
    tags = ('teen','black','amateur')
    orientation = 'Straight'
    
    uploader = KummUploader(domain="http://4tube.com",
                            website="4tube",
                            username="tedwantsmore",
                            http_settings=account.http_settings,
                            drop_incorrect_tags=False,
                            add_all_autocorrect_tags=False,
                            autocorrect_tags=False)
    uploader.upload(video_file,title,pornstars,tags,orientation)
    







