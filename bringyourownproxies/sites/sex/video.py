# -*- coding: utf-8 -*-
#!/usr/bin/python
import re
import path

from bringyourownproxies.video import OnlineVideo,VideoUploadRequest
from bringyourownproxies.errors import InvalidVideoParser
from bringyourownproxies.sites.sex.parser import SexParser

__all__ = ['SexVideoPinRequest','SexVideoPin']

class SexVideoPinRequest(VideoUploadRequest):

    def __init__(self,video_file,title,tags,board,**kwargs):
        self.board = board
        self.sex_tags = kwargs.pop('sex_tags',[])

        super(SexVideoPinRequest,self).__init__(video_file=video_file,
                                                title=title,
                                                tags=tags,
                                                **kwargs)

    def __repr__(self):

        return "<Sex VideoPin Request title:{title} tags:{tags}" \
            " board:{board}>".format(title=self.title.name,
                                                tags=",".join([t.name for t in self.tags]),
                                                board=self.board.name)

class SexVideoPin(OnlineVideo):
    SITE = 'Sex'
    SITE_URL = 'www.sex.com'
    def __init__(self,url=None,title=None,category=None,**kwargs):
        self.pin_id = kwargs.pop('pin_id',None)
        self.sex_parser = kwargs.pop('sex_parser',SexParser())
        self.pinned_date = kwargs.pop('pinned_date',None)
        self.author = kwargs.pop('author',None)
        self.tags = kwargs.pop('tags',None)
        self.total_comments = kwargs.pop('total_comments',None)

        if type(self.sex_parser) != SexParser:
            raise InvalidVideoParser('parser is not a valid SexParser')

        super(SexVideoPin,self).__init__(url=url,title=title,category=category,**kwargs)

    def _get_video_id(self):

        find_video_id = re.match(r'(.*?)/watch/(.*?)/(.*?)',self.url,re.I|re.M)
        if find_video_id:
            return find_video_id.group(2)

    def download(self,**kwargs):
        dir_to_save = kwargs.get('dir_to_save',None)
        name_to_save_as = kwargs.get('name_to_save_as',None)
        video_file = kwargs.get('video_file',0)
        try:
            #verify download dir and file name
            saving_path,filename = self._verify_download_dir(dir_to_save,name_to_save_as)

            go_to_video = self.go_to_video()
            session = self.http_settings.session
            proxy = self.http_settings.proxy
            #grab the raw download url to the video source
            frame_url = self.sex_parser.get_frame_url(go_to_video)
            go_to_video_source = session.get(frame_url,proxies=proxy)

            video_url = self.sex_parser.get_video_pin_url(go_to_video_source.content)
            if type(video_url) == tuple or type(video_url) == list:
                download_video = session.get(video_url[video_file],proxies=proxy)
            else:
                download_video = session.get(video_url,proxies=proxy)

            #create a new file path to where we will save the downloaded movie
            save_at = path.Path.joinpath(saving_path,filename)

            with open(save_at.abspath(),'w+') as f:
                f.write(download_video.content)
        except Exception as exc:
            self.on_failed_download(exception=exc)
            raise exc
        else:
            self.on_success_download(video_url=video_url,video_location=save_at.abspath())

    def get_video_info(self):

        go_to_video = self.go_to_video()
        stats = self.sex_parser.get_video_stats(go_to_video)
        return stats

if __name__ ==  '__main__':
    video = SexVideoPin(url='http://www.sex.com/video/12810676-petplay-video/')
    print video.get_video_info()
    #video.download()
