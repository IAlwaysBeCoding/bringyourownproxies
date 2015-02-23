#!/usr/bin/python
from bringyourownproxies.utils import show_printable_chars
from bringyourownproxies.comment import OnlineComment

class YouPornComment(OnlineComment):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'

    def __init__(self,author,text,comment_id,thumbs_up,thumbs_down,posted_date,**kwargs):

        self.comment_id = comment_id
        self.thumbs_up = thumbs_up
        self.thumbs_down = thumbs_down
        self.posted_date = posted_date
        super(YouPornComment,self).__init__(author=author,text=text,**kwargs)
    
    def __repr__(self):
        return "<{site}'s Comment(author:{a} id:{i} text:{t}...)>".format(site=self.SITE,
                                                                        a=show_printable_chars(self.author),
                                                                        i=self.comment_id,
                                                                        t=show_printable_chars(self.text)[:35])
    
    @classmethod
    def post_comment(cls,account,http_settings):
        pass
        
        

