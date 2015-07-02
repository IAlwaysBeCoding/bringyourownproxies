# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.captcha import DEFAULT_CAPTCHA_SOLVER,DEFAULT_CAPTCHA_MAXIMUM_WAITING
from bringyourownproxies.video import OnlineVideo,VideoUploadRequest,VideoUploaded
from bringyourownproxies.errors import InvalidCategory,InvalidTitle,InvalidDescription

from bringyourownproxies.sites.xhamster.properties import (XhamsterCategoryStraight,
                                                           XhamsterCategoryGay,
                                                           XhamsterCategoryTranssexual,
                                                           XhamsterTitle,
                                                           XhamsterDescription)

__all__ = ['XhamsterVideoUploadRequest','XhamsterVideoUploaded']

class XhamsterVideoUploadRequest(VideoUploadRequest):
    DEFAULT_PASSWORD = "makemoneybitch"
    RECAPTCHA_KEY = '6Ld7YsISAAAAAN-PZ6ABWPR9y5IhwiWbGZgeoqRa'
    def __init__(self,video_file,title,category,description,**kwargs):
        self.is_private = kwargs.get('is_private',False)
        if self.is_private:
            self.password = kwargs.get('password',self.DEFAULT_PASSWORD)
        else:
            self.password = ""

        self.thumbnail_id = kwargs.get('thumbnail_id',1)

        self.allow_comments = kwargs.get('allow_comments',True)
        self.maximum_waiting_time = kwargs.get('maximum_waiting_time',DEFAULT_CAPTCHA_MAXIMUM_WAITING)
        self.captcha_solver = kwargs.get('captcha_solver',DEFAULT_CAPTCHA_SOLVER)
        requirements = [(category,(XhamsterCategoryStraight,XhamsterCategoryGay,XhamsterCategoryTranssexual),InvalidCategory),
                        (title,XhamsterTitle,InvalidTitle),
                        (description,XhamsterDescription,InvalidDescription)]


        self._verify_upload_requirements(requirements)

        super(XhamsterVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        category=category,
                                                        description=description,
                                                        **kwargs)

class XhamsterVideoUploaded(VideoUploaded):
    pass

if __name__ == '__main__':

    def downloading(**kwargs):
        print kwargs

    youporn_video = XhamsterVideo(url='http://www.youporn.com/watch/4543/sexy-black-slut-squirting/?from=search_full&pos=11',
                                iter_size=1048576,
                                hooks={'downloading':downloading})
    #youporn_video.get_video_info()
    #info = youporn_video.get_video_info()
    #print info
    #youporn_video._verify_download_dir('shower.mp4')
    print youporn_video._hooks
    youporn_video.download(name_to_save_as='/root/Dropbox/interracial_pov.mp4')

    #print youporn_video.get_comments()


