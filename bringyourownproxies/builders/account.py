
from bringyourownproxies.sites import (YouPornAccount,DrTuberAccount,HardSexTubeAccount,
                                       PornhubAccount,RedTubeAccount,SexAccount,
                                       TnaflixAccount,XhamsterAccount,XvideosAccount,
                                       SpankwireAccount)
from bringyourownproxies.sites.account import _Account
from bringyourownproxies.builders.base import BaseBuilder
from bringyourownproxies.builders.errors import AccountBuilderException

__all__ = ['AccountBuilder']

class AccountBuilder(BaseBuilder):

    klazz_builder_exception = AccountBuilderException
    klazz_account = _Account

    SITES = {'youporn':YouPornAccount,
             'drtuber':DrTuberAccount,
             'hardsextube':HardSexTubeAccount,
             'pornhub':PornhubAccount,
             'redtube':RedTubeAccount,
             'sex':SexAccount,
             'tnaflix':TnaflixAccount,
             'xhamster':XhamsterAccount,
             'xvideos':XvideosAccount,
             'spankwire':SpankwireAccount}

    def __init__(self,site):
        super(AccountBuilder,self).__init__(site)
        self.factory = self.SITES[site]

    def __call__(self,username,password,email,**kwargs):
        return self.create_account(username=username,
                                   password=password,
                                   email=email,
                                   **kwargs)

    def create_account(self,username,password,email,**kwargs):
        return self.factory(username=username,
                            password=password,
                            email=email,
                            **kwargs)

