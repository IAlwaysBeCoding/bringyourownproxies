# -*- coding: utf-8 -*-
#!/usr/bin/python

from bringyourownproxies.utils import show_printable_chars
from bringyourownproxies.comment import OnlineComment

class MotherlessComment(OnlineComment):
    SITE = 'motherless'
    SITE_URL = 'www.motherless.com'

    def __init__(self,author,text,comment_id,posted_date,links=[],**kwargs):

        self.comment_id = comment_id
        self.posted_date = posted_date
        self.links = links
        super(MotherlessComment,self).__init__(author=author,text=text,**kwargs)

    def __repr__(self):
        return "<{site}'s Comment(author:{a} id:{i} text:{t}...)>".format(site=self.SITE,
                                                                        a=show_printable_chars(self.author),
                                                                        i=self.comment_id,
                                                                        t=show_printable_chars(self.text)[:35])


