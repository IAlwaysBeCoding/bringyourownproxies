#!/usr/bin/python

from bringyourownproxies.author import OnlineAuthor

class YouPornAuthor(OnlineAuthor):
    SITE = 'YouPorn'
    SITE_URL = 'www.youporn.com'
    
    def __init__(self,name,**kwargs):
        super(YouPornAuthor,self).__init__(name=name,**kwargs)
    
    