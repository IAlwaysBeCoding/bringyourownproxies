
from bringyourownproxies.sites import (YouPornUpload,DrTuberUpload,HardSexTubeUpload,
                                       PornhubUpload,RedTubeUpload,SexUploadVideo,
                                       TnaflixUpload,XhamsterUpload,XvideosUpload)

from bringyourownproxies.sites.upload import _Upload
from bringyourownproxies.builders.base import BaseBuilder
from bringyourownproxies.builders.errors import UploadBuilderException

__all__ = ['UploadBuilder']

class UploadBuilder(BaseBuilder):

    klazz_builder_exception = UploadBuilderException
    klazz_upload = _Upload

    SITES = {'youporn':YouPornUpload,
             'drtuber':DrTuberUpload,
             'hardsextube':HardSexTubeUpload,
             "pornhub":PornhubUpload,
             'redtube':RedTubeUpload,
             'sex':SexUploadVideo,
             'tnaflix':TnaflixUpload,
             'xhamster':XhamsterUpload,
             'xvideos':XvideosUpload}

    def __init__(self,site):
        super(UploadBuilder,self).__init__(site)
        self.factory = self.SITES[site]

    def __call__(self,account,video_upload_request,hooks=None,bubble_up_exception=True):
        return self.create_upload(account=account,
                                  video_upload_request=video_upload_request,
                                  hooks=hooks,
                                  bubble_up_exception=True)

    def create_upload(self,account,video_upload_request,hooks=None,bubble_up_exception=True):
        return self.factory(account=account,
                            video_upload_request=video_upload_request,
                            hooks=hooks,
                            bubble_up_exception=True)

