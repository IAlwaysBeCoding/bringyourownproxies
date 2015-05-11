#!/usr/bin/python
import uuid
import io
import functools
import datetime

import path

from bringyourownproxies.errors import (InvalidVideoCallable,InvalidVideoType,VideoFileDoesNotExist,
                                        InvalidTitle,InvalidTag,InvalidCategory,InvalidDescription,
                                        InvalidRequirements,InvalidUploadCallback)
from bringyourownproxies.httpclient import HttpSettings

class VideoObject(object):

    def __init__(self,name="",**kwargs):
        self.name = name

    def __repr__(self):
        return self.name

class Tag(VideoObject):
    pass

class Category(VideoObject):
    pass

class Description(VideoObject):
    pass

class Title(VideoObject):
    pass

class PornStar(VideoObject):
    pass

class Video(object):

    def __init__(self,title=None,category=None,**kwargs):
        self.title = title
        self.category = category

    def __repr__(self):
        return "<Video title:{title} category:{category}>".format(title=self.title,category=self.category)

class OnlineVideo(Video):

    SITE = 'NOT SPECIFIED'
    SITE_URL = None

    DEFAULT_STARTED_CALLBACK = functools.partial(lambda **kwargs: None)
    DEFAULT_DOWNLOADING_CALLBACK = functools.partial(lambda **kwargs : None)
    DEFAULT_FAILED_CALLBACK = functools.partial(lambda **kwargs: None)
    DEFAULT_FINISHED_CALLBACK = functools.partial(lambda **kwargs: None)

    def __init__(self,url,title,category,**kwargs):

        self.url = url
        self.iter_size = kwargs.pop('iter_size') if kwargs.get('iter_size',False) else 1024
        self.http_settings = kwargs.pop('http_settings') if kwargs.get('http_settings',False) else HttpSettings()
        self.bubble_up_exception = kwargs.pop('bubble_up_exception') if kwargs.get('bubble_up_exception',False) else False

        hooks = kwargs.pop('hooks') if kwargs.get('hooks',False) else {}

        self._validate_hooks(hooks)
        self._hooks = {'started':hooks.get('started',self.DEFAULT_STARTED_CALLBACK),
                        'downloading':hooks.get('downloading',self.DEFAULT_DOWNLOADING_CALLBACK),
                        'failed':hooks.get('failed',self.DEFAULT_FAILED_CALLBACK),
                        'finished':hooks.get('finished',self.DEFAULT_FINISHED_CALLBACK)}


        self._started = False
        self._downloading = False
        self._failed = False
        self._finished = False

        super(OnlineVideo,self).__init__(title=title,category=category,**kwargs)

    def has_downloaded_successfully(self):
        return (self._finished and not self._failed and not self._downloading)

    def is_still_downloading(self):
        return (self._started and self._downloading)

    def has_failed(self):
        return (self._started and self._failed)

    def has_started(self):
        return self._started

    def _validate_hooks(self,hooks):

        if not isinstance(hooks,dict):
            raise InvalidVideoCallable('hooks need to be a dictionary with 4 possible callbacks\n'\
                            '\tstarted: called when the download has started\n'\
                            '\tdownloading:called constantly during download\n'\
                            '\tfailed:called when download fails\n'\
                            '\tfinished:called when successfully finished downloading\n')
        for key in hooks:
            if not hasattr(hooks[key],'__call__'):
                raise InvalidVideoCallable('hook:{h} is not a callable'.format(h=key))

    def set_hooks(self,hooks):
        self._validate_hooks(hooks)
        self._hooks.update(hooks)

    def call_hook(self,hook,**kwargs):
        event = getattr(self,"_{hook}".format(hook=hook),None)

        if event is None:
            raise InvalidUploadCallback('Callback does not exist:{event}'.format(event=event))

        event = True
        self._hooks.get(hook)(**kwargs)

    def remove_hook(self,hook):
        event = getattr(self,"_{hook}".format(hook=hook),None)

        if event is None:
            raise InvalidUploadCallback('Callback does not exist:{event}'.format(event=event))

        self._hooks[hook] = getattr(self,'DEFAULT_{hook}_CALLBACK'.format(hook=hook.upper()))

    def _download(self,video_url,file_location):

        session = self.http_settings.session
        proxy = self.http_settings.proxy
        download_video = session.get(video_url,proxies=proxy,stream=True)
        total_length = int(download_video.headers.get('content-length'))

        with open(file_location,'w+') as f:
            total_downloaded = 0
            for part in download_video.iter_content(chunk_size=self.iter_size):
                if part:
                    part_video_data = io.BytesIO(part)
                    total_downloaded += len(part_video_data.getvalue())
                    self.call_hook('downloading',total_downloaded=total_downloaded,
                                                total_size=total_length,
                                                part=part_video_data,
                                                video_url=self.url,
                                                http_settings=self.http_settings,
                                                file=file_location)

                    f.write(part_video_data.getvalue())

    def download(self):
        raise NotImplementedError('Download method must be implemented by classes subclassing from OnlineVideo class')

    def go_to_video(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        #check that the video url belongs to a Youporn.com video, else raise an error.
        if self.SITE_URL not in self.url:
            raise InvalidVideoUrl('Invalid video url, video does not belong to YouPorn.com')

        video = session.get(self.url,proxies=proxy)
        return video.content

    def _verify_download_dir(self,name_to_save_as=None):
        if not name_to_save_as:
            name_to_save_as = str(uuid.uuid4())

        directory = path.Path(name_to_save_as).parent
        path_exists = path.Path(directory).exists()

        if directory == '':
            directory = path.Path(name_to_save_as).getcwd()

        if not path_exists:
            path.Path(directory).makedirs_p()

        return (directory,name_to_save_as)

class VideoUploadRequest(object):

    def __init__(self,
                video_file,
                title=Title(),
                tags=(Tag(),),
                category=Category(),
                description=Description(),
                **kwargs):

        self.video_file = video_file
        self._verify_video_file()

        if not isinstance(title, Title):
            raise InvalidTitle('title is not a valid Title instance')

        if not isinstance(description, Description):
            raise InvalidDescription('description is not a valid Description instance')


        if isinstance(category,(list,tuple)):
            for c in category:
                if not isinstance(c, Category):
                    raise InvalidCategory('c is not a valid Category instance')
        else:
            if not isinstance(category, Category):
                raise InvalidCategory('category is not a valid Category instance')


        if isinstance(tags,(list,tuple)):
            for t in tags:
                if not isinstance(t, Tag):
                    raise InvalidTag('t is not a valid Tag instance')
        else:
            if not isinstance(tags, Tag):
                raise InvalidTag('tags is not a valid Tag instance')

        self.title = title
        self.tags = tags
        self.category = category
        self.description = description
        self._success = None


    def _verify_video_file(self):
        video_path = path.Path(self.video_file)

        if not video_path.isfile():
            raise InvalidVideoType('video_file is not a valid path to a video file')
        if not video_path.exists():
            raise VideoFileDoesNotExist('video_file does not point to a valid file')

    def _verify_upload_requirements(self,requirements):

        if not isinstance(requirements,(list,tuple)):
            raise InvalidRequirements('requirements needs to be a tuple/list containing the' \
                                    '  video upload requirements.Each video requirement ' \
                                    ' needs to have a 4 item tuple.\n' \
                                    ' 1.variable to verify its type\n' \
                                    ' 2.the instance type that the first item needs to be\n' \
                                    ' 3.exception class to raise if variable does not match' \
                                    ' its intended type.')
        for requirement in requirements:

            if not isinstance(requirement,tuple):
                raise InvalidRequirements('Invalid 3 item tuple, missing a valid requirement tuple.'\
                                            'missing var,instance_type,exception_class')

            var,instance_type,exception_class = requirement

            if isinstance(var,(list,tuple)):
                for item in var:
                    if isinstance(instance_type,(list,tuple)):
                        for ins_type in instance_type:
                            if isinstance(item,ins_type):
                                break
                        else:
                            raise exception_class("Invalid {var} type, it contains an " \
                                                    "item inside its list/tuple that is not a valid " \
                                                    " type of either " \
                                                    " {all_types} ".format(var=var,
                                                                            all_types=[tipe for tipe in instance_type]))

                    else:
                        if not isinstance(item,instance_type):
                            raise exception_class("Invalid {var} type, it contains an " \
                                                    "item inside its list/tuple that is not a valid " \
                                                    " type of either:{instance_type}".format(var=var,
                                                                                    instance_type=instance_type))
            else:
                if isinstance(instance_type,(list,tuple)):
                    for ins_type in instance_type:
                        if isinstance(var,ins_type):
                            break
                    else:
                        raise exception_class("Invalid {var} type, is not a valid " \
                                            " type of either:{instance_type}".format(var=var,instance_type=instance_type))

                else:
                    if not isinstance(var,instance_type):
                        raise exception_class("Invalid {var} type, is not a valid " \
                                                " type:{instance_type}".format(var=var,instance_type=instance_type))


    def succeeded(self):
        self._success = True

    def failed(self):
        self._success = False

    def status(self):
        return self._success

class VideoUploaded(object):
    SITE = 'NOT SPECIFIED'
    SITE_URL = None

    def __init__(self,
                url,
                video_id=None,
                title=Title(),
                tags=(Tag(),),
                category=Category(),
                description=Description(),
                username=None,
                date_uploaded=datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                **kwargs):

        if not isinstance(title, Title):
            raise InvalidTitle('title is not a valid Title instance')
        if not isinstance(category, Category):
            raise InvalidCategory('category is not a valid Category instance')
        if not isinstance(description, Description):
            raise InvalidDescription('description is not a valid Description instance')

        if isinstance(tags,(list,tuple)):
            for t in tags:
                if not isinstance(t, Tag):
                    raise InvalidTag('t is not a valid Tag instance')
        else:
            if not isinstance(tags, Tag):
                raise InvalidTag('tags is not a valid Tag instance')


        self.url = url
        self.video_id = video_id
        self.title = title
        self.tags = tags
        self.category = category
        self.description = description
        self.username = username
        self.date_uploaded = date_uploaded

        super(VideoUploaded,self).__init__(**kwargs)



