#!/usr/bin/python

from bringyourownproxies.profile import Profile,BasicProfile,LocationProfile


class YouPornProfile(Profile,BasicProfile,LocationProfile):

    def __init__(self,**kwargs):
        super(YouPornProfile,self).__init__(**kwargs)


    