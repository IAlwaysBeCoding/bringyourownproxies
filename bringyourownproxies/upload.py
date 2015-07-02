# -*- coding: utf-8 -*-
#!/usr/bin/python
import functools

from formatbytes.formatbytes import FormatBytes

from clint.textui.progress import Bar as ProgressBar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.errors import InvalidUploadCallback


class HOOKS(object):

    @staticmethod
    def started(*args,**kwargs):
        pass

    @staticmethod
    def uploading(*args,**kwargs):
        pass

    @staticmethod
    def failed(*args,**kwargs):
        pass

    @staticmethod
    def finished(*args,**kwargs):
        pass


class Upload(object):

    DEFAULT_STARTED_CALLBACK = HOOKS.started
    DEFAULT_UPLOADING_CALLBACK = HOOKS.uploading
    DEFAULT_FAILED_CALLBACK = HOOKS.failed
    DEFAULT_FINISHED_CALLBACK = HOOKS.finished

    def __init__(self,hooks={},bubble_up_exception=False):

        self._validate_hooks(hooks)

        hooks = hooks if hooks is not None else {}
        self._hooks = {'started':hooks.get('started',self.DEFAULT_STARTED_CALLBACK),
                        'uploading':hooks.get('uploading',self.DEFAULT_UPLOADING_CALLBACK),
                        'failed':hooks.get('failed',self.DEFAULT_FAILED_CALLBACK),
                        'finished':hooks.get('finished',self.DEFAULT_FINISHED_CALLBACK)}

        #Should we bubble up exception if any occurs during uploading.
        self.bubble_up_exception = bubble_up_exception

        self._started = False
        self._uploading = False
        self._failed = False
        self._finished = False

        self.upload_monitor = None

    @staticmethod
    def create_multipart_encoder(fields):
        return MultipartEncoder(fields=fields)

    @staticmethod
    def create_multipart_monitor(encoder,callback=None):
        if callback:
            if not hasattr(callback,'__call__'):
                raise InvalidUploadCallback('Callback {c} needs to be callable'.format(c=callback))
            return MultipartEncoderMonitor(encoder,callback)
        else:
            return MultipartEncoderMonitor(encoder)

    def has_uploaded_successfully(self):
        return (self._finished and not self._failed and not self._uploading)

    def is_still_uploading(self):
        return (self._started and self._uploading)

    def has_failed(self):
        return (self._started and self._failed)

    def has_started(self):
        return self._started

    def _validate_hooks(self,hooks):

        if not isinstance(hooks,dict) and hooks is not None:
            raise InvalidUploadCallback('hooks need to be a dictionary with 4 possible callbacks\n'\
                            '\tstarted: called when the upload has started\n'\
                            '\tuploading:called constantly during upload\n'\
                            '\tfailed:called when upload fails\n'\
                            '\tfinished:called when successfully finished uploading\n')

            for key in hooks:
                if not hasattr(hooks[key],'__call__'):
                    raise InvalidUploadCallback('hook:{h} is not a callable'.format(h=key))

    def set_hooks(self,hooks):
        self._validate_hooks(hooks)
        self._hooks.update(hooks)

    def call_hook(self,hook,**kwargs):
        event = getattr(self,"_{hook}".format(hook=hook),None)

        if event is None:
            raise InvalidUploadCallback('Callback does not exist:{event}'.format(event=event))

        event = True

        #Dont call the callback uploading because the monitor will call it
        if hook != 'uploading':
            self._hooks.get(hook)(**kwargs)

    def remove_hook(self,hook):
        event = getattr(self,"_{hook}".format(hook=hook),None)

        if event is None:
            raise InvalidUploadCallback('Callback does not exist:{event}'.format(event=event))

        self._hooks[hook] = getattr(self,'DEFAULT_{hook}_CALLBACK'.format(hook=hook.upper()))

    def start(self):
        raise NotImplementedError('Subclasses need to implement this function,' \
                                   ' which will be the actual uploading function' \
                                   ' for each site')

    def stop(self):
        raise NotImplementedError('Subclasses can implement this function,' \
                                   ' which will stop the current uploading')



