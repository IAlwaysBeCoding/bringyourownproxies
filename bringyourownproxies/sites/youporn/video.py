#!/usr/bin/python
# -*- coding: utf-8 -*-
import uuid
import re

import path


from bringyourownproxies.video import (OnlineVideo,VideoParser,VideoUploadRequest,
                                        VideoUploaded,Tag,Category,Description,Title)
from bringyourownproxies.errors import (InvalidVideoUrl,InvalidVideoParser,InvalidTag,InvalidCategory)
from bringyourownproxies.utils import show_printable_chars

from errors import InvalidYouPornStar
from pornstar import YouPornStar
from author import YouPornAuthor
from comment import YouPornComment

class YouPornTag(Tag):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,name,**kwargs):
        self.href = kwargs.pop('href') if kwargs.get('href',False) else None

        super(YouPornTag,self).__init__(name=name,**kwargs)

class YouPornCategory(Category):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,name,**kwargs):

        self.href = kwargs.pop('href') if kwargs.get('href',False) else None
        self.category_id = kwargs.get('category_id',None)
        if self.category_id is None:
            get_category_id = self._find_category_id(category=name)

            if get_category_id is None and self.href is not None:
                find_category_id = re.match('/(.*?)/(.*?)/(.*?)/',self.href,re.I|re.M)
                if find_category_id:
                    self.category_id = find_category_id.group(2)
                else:
                    raise InvalidCategory('Invalid Category Name, it does not match a category id')
                    
            elif get_category_id is not None:
                self.category_id = get_category_id
            else:

                raise InvalidCategory('Invalid Category Name, it does not match a category id')

            
        super(YouPornCategory,self).__init__(name=name,**kwargs)
    
    def _find_category_id(self,category):

        categories= {'amateur':'1',
                    'hairy': '46',
                     'brunette': '52',
                     'squirting': '39',
                     'german': '58',
                     'bisexual': '5',
                     'handjob': '22',
                     'milf': '29',
                     'fantasy': '42',
                     'pantyhose': '57',
                     'fingering': '62',
                     'asian': '3',
                     'latina': '49',
                     'blonde': '51',
                     'hentai': '23',
                     'rimming': '43',
                     'ebony': '8',
                     'solo male': '60',
                     'interview': '41',
                     'gonzo': '50',
                     'vintage': '33',
                     'threesome': '38',
                     'shaved': '54',
                     'lesbian': '26',
                     'pov': '36',
                     'big butt': '6',
                     'voyeur': '34',
                     'bbw': '4',
                     'fetish': '18',
                     'shemale': '31',
                     'panties': '56',
                     'compilation': '11',
                     'european': '48',
                     'solo girl': '27',
                     'cunnilingus': '15',
                     'gay': '20',
                     'funny': '19',
                     'female friendly': '67',
                     'big tits': '7',
                     'redhead': '53',
                     'blowjob': '9',
                     'creampie': '13',
                     'facial': '17',
                     'kissing': '40',
                     'webcam': '35',
                     'anal': '2',
                     'dp': '16',
                     'couples': '12',
                     'instructional': '24',
                     'romantic': '61',
                     'straight sex': '47',
                     'dildos/toys': '44',
                     'teen': '32',
                     'public': '30',
                     'cumshots': '37',
                     'interracial': '25',
                     'orgy': '21',
                     'mature': '28',
                     'college': '10',
                     'swallow': '59',
                     'massage': '64',
                     'masturbation': '55'}
        
        if category.lower() in categories:
            return categories[category.lower()]

class YouPornVideoParser(VideoParser):
    
    def get_video_stats(self,html):
        
        categories = []
        tags = []
        porn_stars = []
        
        document = self.etree.fromstring(html,self.parser)
        ratings = document.xpath('//div[@class="rating-count"]')[0].text.replace(' ratings)','').replace('(','')
        ratings_percentage = document.xpath('//div[@class="rating-percentage"]')[0] 
        views = document.xpath('//div[@id="stats-views"]/text()')[0].replace(',','')
        uploaded_date = document.xpath('//div[@id="stats-date"]/text()')[0]
        
        get_video_details = document.xpath('//ul[@class="info-list-content"]//a')
        
        for a in get_video_details:
            get_type = re.match(r'/(.*?)/(.*?)/',a.attrib['href'],re.I|re.M)
            if get_type:
                #figure out the type of data, either tag, category or porn star name
                item_type = get_type.group(1)

                if item_type == 'category':
                    #create a new YouPornCategory
                    categories.append(YouPornCategory(name=a.text,href=a.attrib['href']))
                elif item_type == 'porntags':
                    #create a new YouPornTag
                    tags.append(YouPornTag(name=a.text,href=a.attrib['href']))
                elif item_type == 'pornstar':
                    porn_stars.append(YouPornStar(name=a.text,href=a.attrib['href']))
                
        author_name = document.xpath('//button[@data-name]//@data-name')[0]
        author_href = document.xpath('//div[@class="author-block--line"]//a')[0].attrib['href']
        author = YouPornAuthor(name=author_name,href=author_href)
        total_comments =document.xpath('//li[@id="tabComments"]//a[@href="javascript:void(0)"]')[0] \
                         .text.replace('Comments (','').replace(')','')
        
        return {'total_comments':int(total_comments),
                'author':author,
                'porn_stars':porn_stars,
                'categories':categories,
                'tags':tags,
                'uploaded_date':uploaded_date,
                'views':views,
                'ratings':ratings,
                'ratings_percentage':ratings_percentage}
        
    def get_download_url(self,html):
        document = self.etree.fromstring(html,self.parser)
        get_video_url = document.xpath('//video[@id="player-html5"]/@src')
        if get_video_url:
            return get_video_url[0]
    
    def get_all_comments(self,html):
        comments = []
        current_page = None
        total_pages = None
        document = self.etree.fromstring(html,self.parser)

        grab_comments = document.xpath('//li')

        if len(grab_comments):
            for div in grab_comments:
                div_doc = self.etree.fromstring(self.tostring(div),self.parser)
    
                author = div_doc.xpath('//p[@class="name"]')[0].text
                date = div_doc.xpath('//span[@class="date"]/text()')[0].lstrip()
                text = div_doc.xpath('//p[@class="message"]/text()')[0]
                thumbs_up = int(div_doc.xpath('//div[@class="option-links"]/@data-likes')[0])
                thumbs_down = int(div_doc.xpath('//div[@class="option-links"]/@data-dislikes')[0])
                comment_id = div_doc.xpath('//div[@data-commentid]/@data-commentid')[0]
    
                comments.append(YouPornComment(author=author,
                                                text=text,
                                                posted_date=date,
                                                thumbs_up=thumbs_up,
                                                thumbs_down=thumbs_down,
                                                comment_id=comment_id))
            
            get_comments_page = document.xpath('//div[@id="watch-comment-pagination"]//div[@class="pageIndicator"]//text()')
            
            current_page = int(get_comments_page[1])
            total_pages = int(get_comments_page[2].replace(' of ',''))
            
            return (comments,current_page,total_pages)

        else:
            return (None,None,None)

class YouPornVideo(OnlineVideo):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,title=None,category=None,**kwargs):

        self.url = kwargs.pop('url') if kwargs.get('url',False) else None
        self.video_id = kwargs.pop('video_id') if kwargs.get('video_id',False) else self._get_video_id()
        self.video_parser = kwargs.pop('video_parser') if kwargs.get('video_parser',False) else YouPornVideoParser() 
        self.ratings = kwargs.pop('ratings') if kwargs.get('ratings',False) else None
        self.ratings_percentage = kwargs.pop('ratings_percentage') if kwargs.get('ratings_percentage',False) else None
        self.views = kwargs.pop('views') if kwargs.get('views',False) else None
        self.uploaded_date = kwargs.pop('uploaded_date') if kwargs.get('uploaded_date',False) else None
        self.categories = kwargs.pop('categories') if kwargs.get('categories',False) else None 
        self.tags = kwargs.pop('tags') if kwargs.get('tags',False) else None
        self.author = kwargs.pop('author') if kwargs.get('author',False) else None
        self.porn_stars = kwargs.pop('porn_stars') if kwargs.get('porn_stars',False) else None
        self.total_comments = kwargs.pop('total_comments') if kwargs.get('total_comments',False) else None

        if type(self.video_parser) != YouPornVideoParser:
            raise InvalidVideoParser('parser is not a valid YouPornVideoParser')
        super(YouPornVideo,self).__init__(title=title,
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
            raise InvalidVideoUrl('Invalid video url, video does not belong to YouPorn.com')
        
        video = session.get(self.url,proxies=proxy)
        return video.content
        
    def download(self,name_to_save_as=None):

        try:
            #verify download dir and file name
            saving_path,filename = self._verify_download_dir(name_to_save_as)
                    
            go_to_video = self.go_to_video()
            session = self.http_settings.session
            proxy = self.http_settings.proxy
            #grab the raw download url to the video source
            video_url = self.video_parser.get_download_url(go_to_video)
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
        stats = self.video_parser.get_video_stats(go_to_video)
        return stats
    
    def get_comments_from_page(self,page):

        session = self.http_settings.session 
        proxy = self.http_settings.proxy
        url = 'http://www.youporn.com/ajax/'\
                'video/comments/{video_id}/top_comments/'\
                '?page={page}'.format(video_id=self.video_id,page=page)
        get_comments = session.get(url,proxies=proxy)
        
        #parse html and get all comments, returns YouPornComment objects
        comments,current_page,total_pages = self.video_parser.get_all_comments(html=get_comments.content)
        
        return(comments,current_page,total_pages)            
        
    def get_comments(self,start_page=1,end_page=0):
        
        comments = []
        if start_page == 1 and end_page == 0:
            more_pages = True
            
            while more_pages:
                comments_from_page,current_page,total_pages = self.get_comments_from_page(page=start_page)
                comments.extend(comments_from_page)

                if current_page == total_pages:
                    more_pages = False

                start_page += 1
                    
        else:
            for page_num in range(end_page):
                comments_from_page,current_page,total_pages = self.get_comments_from_page(page=page_num)
                comments.extend(comments_from_page)
        
        return comments

class YouPornVideoUploadRequest(VideoUploadRequest):
    DEFAULT_PASSWORD = "makemoneybitch"
    
    def __init__(self,video_file,title,tags,category,description,**kwargs):
        self.is_private = kwargs.get('is_private',False)
        if self.is_private:
            self.password = kwargs.get('password',self.DEFAULT_PASSWORD)
        else:
            self.password = ""
            
        self.allow_comments = kwargs.get('allow_comments',True)
        self.porn_stars = kwargs.get('porn_stars',[])
        
        if type(self.porn_stars) == list or type(self.porn_stars) == tuple:
            for p in self.porn_stars:
                if type(p) != YouPornStar:
                    raise InvalidYouPornStar('Invalid YouPornStar, it needs to be a YouPornStar')
        else:
            if type(self.porn_stars) != YouPornStar:
                raise InvalidYouPornStar('Invalid YouPornStar, it needs to be a YouPornStar')
        
        if type(category) != YouPornCategory:
            raise InvalidCategory('Invalid category, it needs to be a YouPornCategory')

        
        if type(tags) == list or type(tags) == tuple:
            for t in tags:
                if type(t) != YouPornTag:
                    raise InvalidTag('Invalid tag, it needs to be a YouPornTag')
        else:
            if type(tags) != YouPornTag:
                raise InvalidTag('Invalid tag, it needs to be a YouPornTag')
        
        if type(category) != YouPornCategory:
            raise InvalidCategory('Invalid category, it needs to be a YouPornCategory')


        super(YouPornVideoUploadRequest,self).__init__(video_file=video_file,
                                                        title=title,
                                                        tags=tags,
                                                        category=category,
                                                        description=description,
                                                        **kwargs)
        
    def __repr__(self):

        return "<YouPorn UploadRequest title:{title} tags:{tags} category:{category}" \
            " description:{description}>".format(title=self.title.name,
                                                tags=",".join([t.name for t in self.tags]),
                                                category=self.category.name,
                                                description=self.description.name[:25])

    def create_video_settings(self):
        return {"title":str(self.title),
                "description":str(self.description),
                "tags":",".join([t.name for t in self.tags]),
                "porn_stars":",".join([t.name for p in self.porn_stars]),
                "is_private":"1" if self.is_private else "0",
                "password":self.password,
                "allow_comments":"0" if self.allow_comments else "1",
                "category_id":str(self.category.category_id),
                "orientation":"straight"}

class YouPornVideoUploaded(VideoUploaded):
    pass

if __name__ == '__main__':

    youporn_video = YouPornVideo(url='http://www.youporn.com/watch/253391/come-take-a-shower-with-me')
    #youporn_video.get_video_info()
    #info = youporn_video.get_video_info()
    #print info
    #youporn_video._verify_download_dir('shower.mp4')
    youporn_video.download(name_to_save_as='/home/testfiles/shower.mp4')
    #print youporn_video.get_comments()
    
    