# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
import re

from bringyourownproxies.video import VideoUploadRequest,OnlineVideo,VideoUploaded
from bringyourownproxies.errors import InvalidTag,InvalidDescription,InvalidTitle
from bringyourownproxies.sites.xvideos.properties import XvideosTag,XvideosDescription,XvideosTitle

__all__ = ['XvideosVideoUploadRequest','XvideosVideoUploaded','XvideosVideo']
class XvideosVideoUploadRequest(VideoUploadRequest):

    def __init__(self,video_file,title,tags,description,**kwargs):

        self.is_private = kwargs.get('is_private',False)
        self.orientation = kwargs.get('orientation','straight')

        requirements = [(tags,XvideosTag,InvalidTag),
                        (description,XvideosDescription,InvalidDescription),
                        (title,XvideosTitle,InvalidTitle)]

        self._verify_upload_requirements(requirements)

        super(XvideosVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        **kwargs)
    def create_video_settings(self):

    	return {'title':self.title.name,
    			'tags':[t.name for t in self.tags],
    			'is_private':'1' if self.is_private else '0',
    			'description':self.description.name}

class XvideosVideo(OnlineVideo):
    SITE = 'Xvideos'
    SITE_URL = 'www.youporn.com'

    def __init__(self,title=None,category=None,**kwargs):

        self.url = kwargs.pop('url',None)
        self.video_id = kwargs.pop('video_id',self._get_video_id())
        self.video_parser = kwargs.pop('video_parser',XvideosParser())
        self.ratings = kwargs.pop('ratings',None)
        self.ratings_percentage = kwargs.pop('ratings_percentage',None)
        self.views = kwargs.pop('views',None)
        self.uploaded_date = kwargs.pop('uploaded_date',None)
        self.categories = kwargs.pop('categories',None)
        self.tags = kwargs.pop('tags',None)
        self.author = kwargs.pop('author',None)
        self.porn_stars = kwargs.pop('porn_stars',None)
        self.total_comments = kwargs.pop('total_comments',None)

        if not isinstance(self.video_parser,XvideosParser):
            raise InvalidVideoParser('parser is not a valid XvideosParser')

        super(XvideosVideo,self).__init__(title=title,
                                        category=category,
                                        url=self.url,
                                        video_id=self.video_id,
                                        **kwargs)

    def _get_video_id(self):

        find_video_id = re.match(r'(.*?)/watch/(.*?)/(.*?)',self.url,re.I|re.M)
        if find_video_id:
            return find_video_id.group(2)

    def go_to_video(self):
        session = self.http_settings.session
        proxy = self.http_settings.proxy
        #check that the video url belongs to a Youporn.com video, else raise an error.
        if self.SITE_URL not in self.url:
            raise InvalidVideoUrl('Invalid video url, video does not belong to Xvideos.com')

        video = session.get(self.url,proxies=proxy)
        return video.content

    def download(self,name_to_save_as=None):

        try:

            saving_path,filename = self._verify_download_dir(name_to_save_as)
            save_at = path.Path.joinpath(saving_path,filename)

            go_to_video = self.go_to_video()
            session = self.http_settings.session
            proxy = self.http_settings.proxy
            video_url = self.video_parser.get_download_url(go_to_video)
            self._download(video_url,name_to_save_as)

        except Exception as exc:

            self.call_hook('failed',video_url=self.url,
                                    http_settings=self.http_settings,
                                    name_to_save_as=name_to_save_as,
                                    traceback=traceback.format_exc(),
                                    exc_info=sys.exc_info())
            if self.bubble_up_exception:
                raise exc
        else:
            self.call_hook('finished',video_url=self.url,
                                    video_location=save_at.abspath(),
                                    http_settings=self.http_settings,
                                    name_to_save_as=name_to_save_as)

            return True

if __name__ == '__main__':
    import requests
    download = requests.get('http://www.xvideos.com/video11357701/japanese_schoolgirl_bus_chikan')
    parser = XvideosParser()
    download_url = parser.get_download_url(html=download.content)
    video_stats = parser.get_video_stats(html=download.content)
    print video_stats
    print download_url

class XvideosVideoUploaded(VideoUploaded):
    pass

