#!/usr/bin/python

class Comment(object):
    
    def __init__(self,author=None,text=None,**kwargs):
        self.author = author 
        self.text = text
    
    def __repr__(self):
        return "<Comment author:{a} text:{t} >".format(a=self.author,t=self.text)

class OnlineComment(Comment):
    SITE = 'NOT SPECIFIED'
    SITE_URL = None
    
    def __init__(self,author,text,**kwargs):
        super(OnlineComment,self).__init__(author=author,text=text,**kwargs)    
    
    def __repr__(self):
        return "<{site}'s Comment author:{a} text:{t} >".format(site=self.SITE,a=self.author,t=self.text)