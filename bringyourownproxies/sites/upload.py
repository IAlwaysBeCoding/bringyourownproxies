#!/usr/bin/python
import io
import re
import os
import time

import requests
import arrow
import path

from urlobject import URLObject
from lxml import etree
from lxml.etree import HTMLParser,tostring

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from bringyourownproxies.httpclient import HttpSettings
from bringyourownproxies.upload import Upload

from bringyourownproxies.sites.errors import KummProblem,NginxUploaderProblem

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
        get_upload_form = session.get(upload_form_url,proxies=proxy,verify=False)

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
        session.options(posting_url,proxies=proxy,verify=False)

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
                                    proxies=proxy,
                                    verify=False)
        try:
            response = submit_upload.json()
        except:
            raise KummProblem('Expecting json, did not receive json after video uploading')
        else:
            if 'err' in response:
                raise KummProblem('Kumm uploader experienced an error after uploading:{err}'.format(err=response['err']))
            elif 'uuid' in response:
                return response['uuid']

    def upload(self,video_file,title,porn_stars,tags,orientation,callback=None,session=None,proxy=None):

        session = session or self.http_settings.session
        proxy = proxy or self.http_settings.proxy

        uuid = self._upload_video(video_file=video_file,callback=callback,session=session,proxy=proxy)
        if not isinstance(tags,(list,tuple)):
            tags = [tags]
        elif isinstance(tags,tuple):
            tags = list(tags)

        corrected_tags = [( tag,
                            session.get(self._get_correct_tag_url(orientation,tag),proxies=proxy).json())
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


        post = {'sexuality':str(orientation),
                'title':title,
                'porn_stars':porn_stars if porn_stars else "",
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

class NginxUploader(object):

    def __init__(self,domain,**kwargs):

        self.domain = domain
        self.http_settings = kwargs.get('http_settings',HttpSettings())
        self.nginx_uploader_url = kwargs.get('nginx_uploader',
                                             'http://direct.{domain}/admin/' \
                                             'include/uploader_nginx.php'.format(domain=self.domain))

        self._chrsz = 8

    def upload(self,video_file,title,description,categories,tags,is_private,callback=None,session=None,proxy=None,**kwargs):

        session = session or self.http_settings.session
        proxy = proxy or self.http_settings.proxy

        no_tags = kwargs.get('no_tags',False)
        add_content_source_id = kwargs.get('add_content_source_id',False)

        my_video_upload_url = 'http://www.{domain}/my_video_upload/'.format(domain=self.domain)

        go_to_upload = session.get(my_video_upload_url,proxies=proxy)

        doc = etree.fromstring(go_to_upload.content,HTMLParser())


        filehash = self._upload_video(video_file,callback,session,proxy)

        fields = []
        if add_content_source_id:
            found_content_source_id = doc.xpath('//input[@name="content_source_id"]/@value')
            if not found_content_source_id:
                raise NginxUploaderProblem('Cannot find required variable content_source_id')
            content_source_id = found_content_source_id[0]
            fields.append(('content_source_id',str(content_source_id)))


        if not no_tags:
            fields.append(('tags',str(",".join([tag for tag in tags]))))
        fields.append(('action', 'add_new_complete'))
        fields.append(('title',str(title)))
        fields.append(('description',str(description)))
        fields.append(('file',str(path.Path(video_file).name)))
        fields.append(('file_hash',str(filehash)))
        fields.append(('is_private',"1" if is_private else "0"))

        for category in categories:
            fields.append(('category_ids[]',str(category)))
        encoder = MultipartEncoder(fields)

        if callback:
            monitor = MultipartEncoderMonitor(encoder,callback)
        else:
            monitor = MultipartEncoderMonitor(encoder)

        #my_video_upload_url = 'http://httpbin.org/post'
        submit_video = session.post(my_video_upload_url,
                                    data=monitor,
                                    proxies=proxy,
                                    headers={'Content-Type': monitor.content_type})

        with open('nginxuploader.html','w+') as f:
            f.write(submit_video.content)


    def _upload_video(self,video_file,callback,session,proxy):

        session = session or self.http_settings.session
        proxy = proxy or self.http_settings.proxy

        filename = path.Path(video_file).name
        filehash = self._generate_file_hash(filename)
        fields =  []
        fields.append(('filename',filehash))
        fields.append(('content',(path.Path(video_file).name,open(video_file, 'rb'))))

        encoder = MultipartEncoder(fields)

        if callback:
            monitor = MultipartEncoderMonitor(encoder,callback)
        else:
            monitor = MultipartEncoderMonitor(encoder)

        url = '{nginx_uploader_url}?filename={filehash}' \
            '&X-Progress-ID={filehash}'.format(nginx_uploader_url=self.nginx_uploader_url,
                                               filehash=filehash)

        self._get_upload_progress2(filehash)
        upload_video = session.post(url,
                                    data=monitor,
                                    proxies=proxy,
                                    headers={'Content-Type': monitor.content_type})

        return filehash

    def _get_upload_progress(self,filehash):

        session = session or self.http_settings.session
        proxy = proxy or self.http_settings.proxy

        url = 'http://www.{domain}/admin/include/get_upload_status.php?'\
            'filename={filehash}&X-Progress-ID={filehash}'\
            '&rand={timestamp}'.format(domain=self.domain,filehash=filehash,timestamp=self._timestamp())

        get_progress = session.get(url,proxies=proxy)
        print get_progress.content

    def _get_upload_progress2(self,filehash):

        session = self.http_settings.session
        proxy = self.http_settings.proxy

        url = 'http://www.{domain}/get_upload_status2.php?'\
            'X-Progress-ID={filehash}'\
            '&rand={timestamp}'.format(domain=self.domain,filehash=filehash,timestamp=self._timestamp())

        get_progress = session.get(url,proxies=proxy)
        print get_progress.content


    def _generate_file_hash(self,filename):
        return self._encode('{filename}_{timestamp}'.format(filename=filename,timestamp=self._timestamp()))

    def _timestamp(self):
        return int(round(time.time() * 1000))

    def _encode(self,s):
        return self._convert_to_hex(self._algo(self._convert_to_binary(s),len(s) * self._chrsz))

    def _algo(self,x,lin):

        if lin >> 5 > len(x) - 1:
            for i in xrange(len(x)-1,lin >> 5,1):
                x.append(0)
        x[-1] = 0x80 << ((lin) % 32)

        x_index = ((( (lin + 64) & 0xFFFFFFFF )>> 9 ) << 4) + 14
        if x_index > len(x) - 1:
            for i in xrange(len(x)-1,x_index,1):
                x.append(0)
        x[-1] = lin

        copy_of_x = list(x)

        for i in xrange(len(x)-1,256,1):
            x.append(0)

        a = 1732584193
        b = -271733879
        c = -1732584194
        d = 271733878

        for i in xrange(0,len(copy_of_x),16):
            olda = a
            oldb = b
            oldc = c
            oldd = d

            a = self._bbb(a, b, c, d, x[i    ], 7, -680876936)
            d = self._bbb(d, a, b, c, x[i + 1], 12, -389564586)
            c = self._bbb(c, d, a, b, x[i + 2], 17, 606105819)
            b = self._bbb(b, c, d, a, x[i + 3], 22, -1044525330)
            a = self._bbb(a, b, c, d, x[i + 4], 7, -176418897)
            d = self._bbb(d, a, b, c, x[i + 5], 12, 1200080426)
            c = self._bbb(c, d, a, b, x[i + 6], 17, -1473231341)
            b = self._bbb(b, c, d, a, x[i + 7], 22, -45705983)
            a = self._bbb(a, b, c, d, x[i + 8], 7, 1770035416)
            d = self._bbb(d, a, b, c, x[i + 9], 12, -1958414417)
            c = self._bbb(c, d, a, b, x[i + 10], 17, -42063)
            b = self._bbb(b, c, d, a, x[i + 11], 22, -1990404162)
            a = self._bbb(a, b, c, d, x[i + 12], 7, 1804603682)
            d = self._bbb(d, a, b, c, x[i + 13], 12, -40341101)
            c = self._bbb(c, d, a, b, x[i + 14], 17, -1502002290)
            b = self._bbb(b, c, d, a, x[i + 15], 22, 1236535329)
            a = self._ccc(a, b, c, d, x[i + 1], 5, -165796510)
            d = self._ccc(d, a, b, c, x[i + 6], 9, -1069501632)
            c = self._ccc(c, d, a, b, x[i + 11], 14, 643717713)
            b = self._ccc(b, c, d, a, x[i   ], 20, -373897302)
            a = self._ccc(a, b, c, d, x[i + 5], 5, -701558691)
            d = self._ccc(d, a, b, c, x[i + 10], 9, 38016083)
            c = self._ccc(c, d, a, b, x[i + 15], 14, -660478335)
            b = self._ccc(b, c, d, a, x[i + 4], 20, -405537848)
            a = self._ccc(a, b, c, d, x[i + 9], 5, 568446438)
            d = self._ccc(d, a, b, c, x[i + 14], 9, -1019803690)
            c = self._ccc(c, d, a, b, x[i + 3], 14, -187363961)
            b = self._ccc(b, c, d, a, x[i + 8], 20, 1163531501)
            a = self._ccc(a, b, c, d, x[i + 13], 5, -1444681467)
            d = self._ccc(d, a, b, c, x[i + 2], 9, -51403784)
            c = self._ccc(c, d, a, b, x[i + 7], 14, 1735328473)
            b = self._ccc(b, c, d, a, x[i + 12], 20, -1926607734)
            a = self._ddd(a, b, c, d, x[i + 5], 4, -378558)
            d = self._ddd(d, a, b, c, x[i + 8], 11, -2022574463)
            c = self._ddd(c, d, a, b, x[i + 11], 16, 1839030562)
            b = self._ddd(b, c, d, a, x[i + 14], 23, -35309556)
            a = self._ddd(a, b, c, d, x[i + 1], 4, -1530992060)
            d = self._ddd(d, a, b, c, x[i + 4], 11, 1272893353)
            c = self._ddd(c, d, a, b, x[i + 7], 16, -155497632)
            b = self._ddd(b, c, d, a, x[i + 10], 23, -1094730640)
            a = self._ddd(a, b, c, d, x[i + 13], 4, 681279174)
            d = self._ddd(d, a, b, c, x[i   ], 11, -358537222)
            c = self._ddd(c, d, a, b, x[i + 3], 16, -722521979)
            b = self._ddd(b, c, d, a, x[i + 6], 23, 76029189)
            a = self._ddd(a, b, c, d, x[i + 9], 4, -640364487)
            d = self._ddd(d, a, b, c, x[i + 12], 11, -421815835)
            c = self._ddd(c, d, a, b, x[i + 15], 16, 530742520)
            b = self._ddd(b, c, d, a, x[i + 2], 23, -995338651)
            a = self._eee(a, b, c, d, x[i   ], 6, -198630844)
            d = self._eee(d, a, b, c, x[i + 7], 10, 1126891415)
            c = self._eee(c, d, a, b, x[i + 14], 15, -1416354905)
            b = self._eee(b, c, d, a, x[i + 5], 21, -57434055)
            a = self._eee(a, b, c, d, x[i + 12], 6, 1700485571)
            d = self._eee(d, a, b, c, x[i + 3], 10, -1894986606)
            c = self._eee(c, d, a, b, x[i + 10], 15, -1051523)
            b = self._eee(b, c, d, a, x[i + 1], 21, -2054922799)
            a = self._eee(a, b, c, d, x[i + 8], 6, 1873313359)
            d = self._eee(d, a, b, c, x[i + 15], 10, -30611744)
            c = self._eee(c, d, a, b, x[i + 6], 15, -1560198380)
            b = self._eee(b, c, d, a, x[i + 13], 21, 1309151649)
            a = self._eee(a, b, c, d, x[i + 4], 6, -145523070)
            d = self._eee(d, a, b, c, x[i + 11], 10, -1120210379)
            c = self._eee(c, d, a, b, x[i + 2], 15, 718787259)
            b = self._eee(b, c, d, a, x[i + 9], 21, -343485551)
            a = self._add(a,olda)
            b = self._add(b,oldb)
            c = self._add(c,oldc)
            d = self._add(d,oldd)

        return [a,b,c,d]

    def _aaa(self,q,a,b,x,s,t):
        a_q = self._add(a,q)
        x_t = self._add(x,t)

        add = self._add(a_q,x_t)
        rol = self._rol(add,s)

        ret = self._add(rol,b)

        return ret

    def _bbb(self,a,b,c,d,x,s,t):
        ret = self._aaa((b & c) | ((~b) & d),a,b,x,s,t)
        return ret

    def _ccc(self,a,b,c,d,x,s,t):
        return self._aaa((b & d) | ( c & (~d)),a,b,x,s,t)

    def _ddd(self,a,b,c,d,x,s,t):
        return self._aaa(b ^ c ^ d,a,b,x,s,t)

    def _eee(self,a,b,c,d,x,s,t):
        return self._aaa(c^(b|(~d)),a,b,x,s,t)

    def _add(self,x,y):
        lsw = (x & 0xFFFF) + (y & 0xFFFF)
        msw = (x >> 16) + (y >> 16 ) + (lsw >> 16)
        return ( msw << 16) | ( lsw & 0xFFFF)

    def _rol(self,num,cnt):
        ret = (num << cnt) | ((num & 0xFFFFFFFF ) >> (32 - cnt))
        return ret

    def _convert_to_binary(self,string):
        _bin = []
        self._chrsz = 8
        mask = (1  << self._chrsz) - 1

        for i in xrange(0,(len(string)*8)-1,self._chrsz):
            char_code = int(format(ord(string[i/self._chrsz])))
            bin_data = char_code << (i % 32)
            if ((i >> 5) +1) > len(_bin):
                _bin.append(bin_data)
            else:
                _bin[i >> 5] |= bin_data

        return _bin

    def _convert_to_hex(self,binarray):
        hex_tab = '0123456789abcdef'
        string = ''
        for i in xrange(0,(len(binarray)*4),1):
            a = (binarray[i >> 2] >> ((i%4) * 8 + 4)) & 0xF
            b = (binarray[i >> 2] >> ((i%4) * 8))  & 0xF

            hex_tab_a = hex_tab[a]
            hex_tab_b = hex_tab[b]

            string += hex_tab_a+hex_tab_b

        return string

if __name__ == '__main__':
    from bringyourownproxies.sites import PrivateHomeClipsAccount,TubeCupAccount,HdZogAccount,MyLustAccount
    account = MyLustAccount(username="tedwantsmore",password="money1003",email="tedwantsmore@gmx.com")
    account.login()

    http_settings = account.http_settings

    def progress(monitor):
        pass

    video_file = '/root/Dropbox/craigslistbitch.mp4'
    title = 'Hot girl taking a shower'
    description = 'super hot girl taking a shower'
    tags = ('teen','black','amateur')
    categories = (24,232)
    is_private = False
    uploader = NginxUploader(domain='mylust.com',http_settings=http_settings)
    nginx_uploader_url = 'http://mylust.com/uploader_nginx.php'
    uploader.upload(video_file,
                    title,
                    description,
                    categories,
                    tags,
                    is_private,
                    callback=progress,
                    add_screenshot=True,
                    no_tags=True,
                    nginx_uploader_url=nginx_uploader_url)






