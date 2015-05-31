# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
"""
from formatbytes.formatbytes import FormatBytes
from clint.textui.progress import Bar as ProgressBar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
 
import requests
 
COUNT = 0
def create_callback(encoder):
    encoder_len = len(encoder)

    bar = ProgressBar(expected_size=encoder_len, filled_char='=')
 
    def callback(monitor):
        global COUNT
        COUNT += 1 
        print COUNT
        f = FormatBytes()
        result = f.format(bytes=monitor.bytes_read, unit='KB', precision=0, comma=True)
        print type(result)
        print type(monitor.bytes_read)
        bar.show(monitor.bytes_read)
 
    return callback
 
#first_file = '/home/ubuntu/workspace/testfiles/goodgirl.mp4'
second_file = '/home/ubuntu/workspace/testfiles/daughter.mp4'
#second_file = '/home/ubuntu/workspace/test/test.txt'
def create_upload():
    from requests_toolbelt.multipart.encoder import CustomBytesIO
    m = MultipartEncoder({
        'form_field': 'value',
        'another_form_field': 'another value',
        #'first_file': ('progress_bar.py', open(first_file, 'rb')),
        'second_file': ('progress_bar.py', open(second_file, 'rb')),
        })
    m._buffer = CustomBytesIO(encoding='utf-8')    
    return m
 

if __name__ == '__main__':
    encoder = create_upload()
    callback = create_callback(encoder)
    monitor = MultipartEncoderMonitor(encoder, callback)
    r = requests.post('https://httpbin.org/post', data=monitor,
                      headers={'Content-Type': monitor.content_type})
    print('\nUpload finished! (Returned status {0} {1})'.format(
        r.status_code, r.reason
        ))
from gevent import monkey

gevent.monkey.patch_all()
monkey.patch_all()

class BaseUploader(object):
    pass


class MultiUploader(BaseUploader):
    pass

class UploadMonitor(object):
    pass


#ability to ke
#should have hooks for failed,success upload
#should have a gevent pool
#should have a monitor
#should have a queue
"""