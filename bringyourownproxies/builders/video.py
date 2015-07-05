from bringyourownproxies.sites import SexBoard
from bringyourownproxies.sites import (YouPornVideoUploadRequest,DrTuberVideoUploadRequest,
                                       HardSexTubeVideoUploadRequest,PornhubVideoUploadRequest,
                                       RedTubeVideoUploadRequest,SexVideoPinRequest,
                                       TnaflixVideoUploadRequest,XhamsterVideoUploadRequest,
                                       XvideosVideoUploadRequest)


from bringyourownproxies.builders.base import BaseBuilder
from bringyourownproxies.builders.errors import VideoRequestBuilderException
from bringyourownproxies.builders.properties import (TagBuilder,CategoryBuilder,
                                                    DescriptionBuilder,TitleBuilder)

class VideoRequestBuilder(BaseBuilder):

    klazz_builder_exception = VideoRequestBuilderException
    BUILDERS = {'tag':TagBuilder,
                'category':CategoryBuilder,
                'title':TitleBuilder,
                'description':DescriptionBuilder
                }

    SITES = {'youporn':{
                        'video_upload_request':YouPornVideoUploadRequest,
                        'multiple':{'tag':True,'category':False}
                        },
             'drtuber':{
                        'video_upload_request':DrTuberVideoUploadRequest,
                        'multiple':{'tag':True,'category':False}
                        },
             'hardsextube':{
                            'video_upload_request':HardSexTubeVideoUploadRequest,
                            'multiple':{'tag':True,'category':False}
                        },
             'pornhub':{
                        'video_upload_request':PornhubVideoUploadRequest,
                        'multiple':{'tag':True,'category':True}
                        },
             'redtube':{
                        'video_upload_request':RedTubeVideoUploadRequest,
                        'multiple':{'tag':True,'category':True}
                        },
             'sex':{
                    'board':SexBoard,
                    'video_upload_request':SexVideoPinRequest,
                    'multiple':{'tag':True,'category':False}
                    },
             'tnaflix':{
                        'video_upload_request':TnaflixVideoUploadRequest,
                        'multiple':{'tag':True,'category':False}
                        },
             'xhamster':{
                        'video_upload_request':XhamsterVideoUploadRequest,
                         'multiple':{'tag':False,'category':True}
                         },
             'xvideos':{
                        'video_upload_request':XvideosVideoUploadRequest,
                        'multiple':{'tag':True,'category':False}
                        }
             }

    def __init__(self,site):

        super(VideoRequestBuilder,self).__init__(site)
        for builder in self.BUILDERS:
            self.BUILDERS[builder] = self.BUILDERS[builder](site)

        if site == 'sex':
            self.BUILDERS['sex'] = SexBoard

    def __call__(self,video_file,**kwargs):
        return self.create_upload_request(video_file=video_file,
                                          **kwargs)

    def _get_builder(self,property_type):
        return self.BUILDERS.get(property_type,False)

    def _create_property(self,property_type,property_values):

        builder = self._get_builder(property_type)
        if builder is None:
            return None
        if builder == False:
            raise VideoRequestBuilderException('There is no builder for ' \
                                               ' property {b} '.format(b=property_type))
        if isinstance(property_values,dict):
            return builder(**property_values)
        else:
            return builder(property_values)

    def _build_properties(self,properties):

        processed = {}

        for property_type in properties:
            builder = self._get_builder(property_type)
            if not builder:
                continue

            raw_value = properties[property_type]
            if isinstance(raw_value,(tuple,list)):
                if len(raw_value) == 1:
                    processed[property_type] = self._create_property(property_type=property_type,
                                                                     property_values=raw_value[0])
                else:
                    if self.SITES[self.site]['multiple'][property_type] == False:
                        raise VideoRequestBuilderException('Video Request does not support ' \
                                                            'multiple {k} properties , ' \
                                                            'a list or tuple was given ' \
                                                            'instead of one item'.format(k=property_type))

                    processed[property_type] = [self._create_property(property_type=property_type,
                                                                      property_values=item) for item in raw_value]

            else:
                built = self._create_property(property_type=property_type,
                                              property_values=raw_value)
                if built is not None:
                    processed[property_type] = built
        return processed

    def _build_request(self,video_file,**properties):
        klazz = self.SITES[self.site]['video_upload_request']

        if 'tag' in properties:
            properties['tags'] = properties['tag']
            del properties['tag']
        if self.site == 'sex':
            properties['sex_tags'] = properties['tags']
        request = klazz(video_file,**properties)
        return request

    def create_upload_request(self,video_file,**kwargs):

        properties = self._build_properties(kwargs)
        kwargs.update(properties)
        video_upload_request = self._build_request(video_file,**kwargs)
        return video_upload_request

