# -*- coding: utf-8 -*-
#!/usr/bin/python

class Author(object):

    def __init__(self,name=None,**kwargs):
        self.name = name

    def __repr__(self):
        return '<Author:{s}>'.format(s=self.name)

class OnlineAuthor(Author):
    SITE = 'NOT SPECIFIED'
    SITE_URL = None

    def __init__(self,name,**kwargs):
        self.href = kwargs.pop('href',None)

        super(OnlineAuthor,self).__init__(name=name,**kwargs)

    def __repr__(self):
        return """<{site}'s Author:{s} href:{h}>""".format(site=self.SITE,s=self.name,h=self.href)
