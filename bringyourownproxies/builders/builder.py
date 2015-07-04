
from bringyourownproxies.video import (Title,Category,Tag,Description)
from bringyourownproxies.sites import (YouPornTag,YouPornCategory,YouPornDescription,
                                       YouPornTitle,YouPornVideoUploadRequest,
                                       YouPornUpload,YouPornAccount)

from bringyourownproxies.sites import (DrTuberTitle,DrTuberTag,DrTuberDescription,
                                       DrTuberCategoryStraight,DrTuberCategoryGay,
                                       DrTuberCategoryTranssexual,DrTuberAccount,
                                       DrTuberVideoUploadRequest,DrTuberUpload)

from bringyourownproxies.sites import (HardSexTubeTitle,HardSexTubeDescription,
                                      HardSexTubeTag,HardSexTubeCategoryStraight,
                                      HardSexTubeCategoryGay,HardSexTubeCategoryTranssexual,
                                      HardSexTubeVideoUploadRequest,HardSexTubeUpload,
                                      HardSexTubeAccount)

from bringyourownproxies.sites import (PornhubTitle,PornhubTag,PornhubCategory,
                                       PornhubUpload,PornhubVideoUploadRequest,
                                       PornhubAccount)

from bringyourownproxies.sites import (RedTubeAccount,RedTubeTitle,
                                        RedTubeTag,RedTubeVideoUploadRequest,
                                        RedTubeUpload)

from bringyourownproxies.sites import (SexVideoPinRequest,SexUploadVideo,
                                       SexTag,SexTitle,SexBoard,SexAccount)

from bringyourownproxies.sites import (TnaflixVideoUploadRequest,TnaflixAccount,
                                       TnaflixTitle,TnaflixDescription,
                                       TnaflixTag,TnaflixCategory,TnaflixUpload)

from bringyourownproxies.sites import (XhamsterCategoryStraight,XhamsterCategoryGay,
                                        XhamsterCategoryTranssexual,XhamsterTitle,
                                        XhamsterDescription,XhamsterVideoUploadRequest,
                                        XhamsterUpload,XhamsterAccount)

from bringyourownproxies.sites import (XvideosVideoUploadRequest,XvideosUpload,
                                       XvideosAccount,XvideosTag,
                                       XvideosDescription,XvideosTitle)

from bringyourownproxies.sites.account import _Account
from bringyourownproxies.sites.upload import _Upload

class BuilderException(Exception):
    pass

class UploadBuilderException(BuilderException):
    pass

class AccountBuilderException(BuilderException):
    pass

class VideoRequestBuilderException(BuilderException):
    pass

class BaseBuilder(object):

    klazz_builder_exception = BuilderException
    _site = None
    SITES = {}

    def __init__(self,site):

        if not self.is_site_supported(site):
            raise self.klazz_builder_exception('Site :{s}' \
                                                'is not supported' \
                                                ''.format(s=site))
        self._site = site

    @property
    def site(self):
        return self._site

    def is_site_supported(self,site):
        if not self.SITES.get(site,None):
            return False
        else:
            return True

    def _get_build_method(self,name):

        builder_method = 'create_{t}'.format(t=name)
        method = getattr(self,builder_method)
        return method

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
        self.klazz_upload = self.SITES[site]

    def create_upload(self,account,video_upload_request,hooks=None,bubble_up_exception=True):
        return self.klazz_upload(account=account,
                                video_upload_request=video_upload_request,
                                hooks=hooks,
                                bubble_up_exception=True)

class AccountBuilder(BaseBuilder):

    klazz_builder_exception = AccountBuilderException
    klazz_account = _Account
    SITES = {'youporn':YouPornAccount,
             'drtuber':DrTuberAccount,
             'hardsextube':HardSexTubeAccount,
             'pornhub':PornhubAccount,
             'redtube':RedTubeAccount,
             'sex':SexAccount,
             'tnaflix':TnaflixAccount,
             'xhamster':XhamsterAccount,
             'xvideos':XvideosAccount}

    def __init__(self,site):
        super(AccountBuilder,self).__init__(site)
        self.klazz_account = self.SITES[site]

    def create_account(self,username,password,email,**kwargs):
        return self.klazz_account(username=username,
                                password=password,
                                email=email,
                                **kwargs)

class VideoRequestBuilder(BaseBuilder):

    klazz_builder_exception = VideoRequestBuilderException
    klazz_tag = Tag
    klazz_category = Category
    klazz_title = Title
    klazz_description = Description

    SITES = {'youporn':{'tag':YouPornTag,
                        'category':YouPornCategory,
                        'description':YouPornDescription,
                        'title':YouPornTitle,
                        'video_upload_request':YouPornVideoUploadRequest,
                        'multiple':{'tags':True,'categories':False}
                        },
             'drtuber':{'tag':DrTuberTag,
                        'category':{'straight':DrTuberCategoryStraight,
                                      'gay':DrTuberCategoryGay,
                                      'transsexual':DrTuberCategoryTranssexual},
                        'description':DrTuberDescription,
                        'title':DrTuberTitle,
                        'video_upload_request':DrTuberVideoUploadRequest,
                        'multiple':{'tags':True,'categories':False}
                        },
             'hardsextube':{'tag':HardSexTubeTag,
                            'category':{'straight':HardSexTubeCategoryStraight,
                                          'gay':HardSexTubeCategoryGay,
                                          'transsexual':HardSexTubeCategoryTranssexual},
                            'description':HardSexTubeDescription,
                            'title':HardSexTubeTitle,
                            'video_upload_request':HardSexTubeVideoUploadRequest,
                            'multiple':{'tags':True,'categories':False}
                        },
             'pornhub':{'tag':PornhubTag,
                        'category':PornhubCategory,
                        'description':None,
                        'title':PornhubTitle,
                        'video_upload_request':PornhubVideoUploadRequest,
                        'multiple':{'tags':True,'categories':True}
                        },
             'redtube':{'tag':RedTubeTag,
                        'category':None,
                        'description':None,
                        'title':RedTubeTitle,
                        'video_upload_request':RedTubeVideoUploadRequest,
                        'multiple':{'tags':True,'categories':True}
                        },
             'sex':{'tag':SexTag,
                    'category':None,
                    'description':None,
                    'title':SexTitle,
                    'board':SexBoard,
                    'video_upload_request':SexVideoPinRequest,
                    'multiple':{'tags':True,'categories':False}
                    },
             'tnaflix':{'tag':TnaflixTag,
                        'category':TnaflixCategory,
                        'description':TnaflixDescription,
                        'title':TnaflixTitle,
                        'video_upload_request':TnaflixVideoUploadRequest,
                        'multiple':{'tags':True,'categories':False}
                    },
             'xhamster':{'tag':None,
                         'category':{'straight':XhamsterCategoryStraight,
                                     'gay':XhamsterCategoryGay,
                                     'transsexual':XhamsterCategoryTranssexual},
                         'description':XhamsterDescription,
                         'title':XhamsterTitle,
                         'video_upload_request':XhamsterVideoUploadRequest,
                         'multiple':{'tags':False,'categories':True}
                         },
             'xvideos':{'tag':XvideosTag,
                        'category':None,
                        'description':XvideosDescription,
                        'title':XvideosTitle,
                        'video_upload_request':XvideosVideoUploadRequest,
                        'multiple':{'tags':True,'categories':False}
                        }
             }

    def __init__(self,site):

        super(VideoRequestBuilder,self).__init__(site)

        self.klazz_tag = self.SITES[site]['tag']
        self.klazz_category = self.SITES[site]['category']
        self.klazz_title = self.SITES[site]['title']
        self.klazz_description = self.SITES[site]['description']

        if site == 'sex':
            self.SITES[site]['board'] = SexBoard
            self.klazz_board = self.SITES[site]

    def get_category_type(self,options):
        category_type = options.get('category_type',None)

        if not category_type:
            raise VideoRequestBuilderException('Missing category_type')

        return category_type

    def find_category_class(self,site_name,category):
        site = self.SITES.get(site_name,None)
        if not site:
            raise VideoRequestBuilderException('site_name does ' \
                                                'not exist.')

        if not isinstance(site['category'],dict):
            raise VideoRequestBuilderException('Categories does not include a' \
                                                ' dict of categories to choose ' \
                                                ' from')

        klazz_category = site['category'].get(category,None)
        if not klazz_category:
            raise VideoRequestBuilderException('Could not find a category class ' \
                                                'for category:{c}'.format(c=category))

        return klazz_category

    def create_tag(self,tag,**kwargs):
        return self.klazz_tag(name=tag,**kwargs)

    def create_category(self,category,**kwargs):
        if isinstance(self.klazz_category,dict):

            category_type = self.get_category_type(options=kwargs)
            klazz_category = self.find_category_class(site_name=self.site,
                                                      category=category_type)
            self.klazz_category = klazz_category

        return self.klazz_category(name=category,**kwargs)

    def create_title(self,title,**kwargs):
        return self.klazz_title(name=title,**kwargs)

    def create_description(self,description,**kwargs):
        return self.klazz_description(name=description,**kwargs)

    def create_upload_request(self,video_file,**kwargs):

        def build_properties(request,**kwargs):
            properties = {}
            delete = []
            for key in request:
                if request[key]:

                    if key == 'board':

                        klazz_board = self.SITES['sex']['board']
                        board_id = request[key]['board_id']
                        board_name = request[key]['board_name']

                        board = klazz_board(name=board_name,
                                            board_id=board_id)
                        properties['board'] = board
                        continue

                    found_property = self.SITES[self.site].get(key,False)
                    if found_property == False:
                        raise VideoRequestBuilderException('Property {k} '\
                                                           ' class not found '\
                                                           ' for VideoUploadRequest' \
                                                           ''.format(k=key))
                    elif found_property is None:
                        properties[key] = None
                        delete.append(key)
                        continue

                    create = self._get_build_method(key)

                    if isinstance(request[key],(tuple,list)):
                        properties[key] = [create(item,**kwargs) for item in request[key]]
                    else:
                        multiple_keys_supported = [supported
                                                    for supported in self.SITES[self.site]['multiple']
                                                    if supported]

                        if key in multiple_keys_supported:
                            properties[key] = [create(request[key],**kwargs)]
                        else:
                            properties[key] = create(request[key],**kwargs)

            for delete_key in delete:
                del properties[delete_key]
            return properties

        def build_request(properties):

            klazz = self.SITES[self.site]['video_upload_request']

            if 'tag' in properties:
                properties['tags'] = properties['tag']
                del properties['tag']
            if self.site == 'sex':
                properties['sex_tags'] = properties['tags']

            request = klazz(**properties)
            return request


        request = {'description':kwargs.pop('description',None),
                   'title':kwargs.pop('title',None),
                   'tag':kwargs.pop('tag',None),
                   'category':kwargs.pop('category',None)
                   }

        if kwargs.get('board',None):
            request['board'] = kwargs.pop('board',None)
            if not isinstance(request['board'],dict):
                raise VideoRequestBuilderException('Missing dictionary of '\
                                                   'board_id and board_name '\
                                                   ' to pin up video request')
            if 'board_id' not in request['board']:
                raise VideoRequestBuilderException('Missing board_id')

            if 'board_name' not in request['board']:
                raise VideoRequestBuilderException('Missing board_name')


        params = build_properties(request=request,**kwargs)
        params['video_file'] = video_file
        params.update(kwargs)

        video_upload_request = build_request(properties=params)

        return video_upload_request


if __name__ == '__main__':
    from clint.textui.progress import Bar as ProgressBar
    import path
    site = 'xhamster'
    f = {'account':AccountBuilder(site),
         'upload':UploadBuilder(site),
         'video':VideoRequestBuilder(site)
        }
    username = 'tedwantsmore'
    password = 'money1003'
    email = 'tedwantsmore@gmx.com'
    description = 'Milf loves this anal'
    title = 'Big Boob Milf Loves Anal'
    categories = 'amateur'
    tags  = ('anal','amateur','milf')
    video_file = '/home/testfiles/milf_loves_anal.mp4'
    allow_comments = False
    category_type = 'transsexual'
    size = path.Path(video_file).size
    bar = ProgressBar(expected_size=size,filled_char='*')
    board = {'board_name':'girls','board_id':696286}
    def started(*args,**kwargs):
        video_upload_request = kwargs.get('video_upload_request')
        import time
        # at the beginning:
        start_time = time.time()


        print 'STARTED uploading video:{title}\n' \
                'tags:{tags}\n' \
                'category:{category}\n' \
                'description:{description}\n' \
                .format(title=video_upload_request.title,
                        tags=video_upload_request.tags,
                        category=video_upload_request.category,
                        description=video_upload_request.description)

    def uploading(*args,**kwargs):
        monitor = args[0]
        bar.show(monitor.bytes_read)
        #bar.show(monitor.bytes_read)

    def failed(*args,**kwargs):
        print 'FAILED'

    def finished(*args,**kwargs):
        print kwargs
        global start_time
        import time
        #print("it took %f seconds" % (time.time() - start_time))
        print 'FINISHED'



    request = f['video'].create_upload_request(video_file=video_file,
                                                description=description,
                                                title=title,
                                                tag=tags,
                                                category=categories,
                                                allow_comments=False,
                                                category_type=category_type,
                                                board=board)

    account = f['account'].create_account(username=username,
                                            password=password,
                                            email=email)

    upload = f['upload'].create_upload(account=account,
                                        video_upload_request=request,
                                        hooks={'started':started,
                                                 'uploading':uploading,
                                                 'failed':failed,
                                                 'finished':finished})

    account.login()
    print account.is_logined()
    #account.save_cookies('/root/Dropbox/youporn_cookies.txt')
    #account.load_cookies('/root/Dropbox/youporn_cookies.txt')
    upload.start()
