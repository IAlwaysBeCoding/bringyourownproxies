#!/usr/bin/python
from bringyourownproxies.utils import show_printable_chars
from bringyourownproxies.comment import OnlineComment

__all__ = ['SexComment']

class SexComment(OnlineComment):
    SITE = 'Sex'
    SITE_URL = 'www.sex.com'

    def __init__(self,author,text,author_avatar,author_href,**kwargs):
        
        super(SexComment,self).__init__(author=author,text=text,**kwargs)
    
    def __repr__(self):
        return "<{site}'s Comment(author:{a} text:{t}...)>".format(site=self.SITE,
                                                                    a=show_printable_chars(self.author),
                                                                    t=show_printable_chars(self.text)[:35])
    
    @classmethod
    def post_comment(cls,account,http_settings):
        pass
        
        

