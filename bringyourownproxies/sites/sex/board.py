#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from lxml import etree
from lxml.etree import HTMLParser,tostring

from bringyourownproxies.errors import InvalidAccount,NotLogined
from bringyourownproxies.sites.sex.errors import BoardProblem,BoardAlreadyTaken
from bringyourownproxies.sites.sex.account import SexAccount

__all__ = ['SexBoard']

class SexBoard(object):
    
    def __init__(self,name,board_id,**kwargs):
        self.name = name
        self.board_id = board_id
        self.description = kwargs.get('description','')

    @classmethod
    def create(cls,name,description,account):
        
        session = account.http_settings.session
        proxy = account.http_settings.proxy
        if type(account) != SexAccount:
            raise InvalidAccount('Invalid account, '\
                                                'it needs to be a SexAccount instance')
        if not account.is_logined():
            raise NotLogined('Sex account is not logined')
        
        create_board_form = session.get('http://www.sex.com/board/edit',proxies=proxy)
        post = {'name':name,'description':description,'submit':'Create Board'}
        create_new_board = session.post('http://www.sex.com/board/edit',data=post,proxies=proxy)
        doc = etree.fromstring(create_new_board.content,HTMLParser())
        find_errors = doc.xpath('//div[@class="error"]/text()')


        if find_errors:
            if find_errors[0] == 'Already Taken':
                raise BoardAlreadyTaken('Board: "{b}" already taken'.format(b=name))
            else:
                raise BoardProblem('Error while creating a new Board:"{b}" Error Message:{e}'.format(b=name,e=find_errors[0]))

        boards = doc.xpath('//div[@class="masonry_box small_board_box"]')
        for board in boards:
            board_doc = etree.fromstring(tostring(board),HTMLParser())
            get_title = board_doc.xpath('//div[@class="title"]//strong')

            if not get_title:
                raise BoardProblem('Cannot find new board name that was created')
                
            if get_title[0].text == name:
                get_board_id = board_doc.xpath('//a[@class="btn btn-block"]/@href')

                if not get_board_id:
                    raise BoardProblem('Cannot find new board id that was created')
                
                board_id = get_board_id[0].replace('/board/edit/','')
                return cls(name=name,board_id=board_id,description=description)                

        raise BoardProblem('Could not find board name inside dashboard')        
        


def create_board():
    pass

if __name__ == '__main__':
    from bringyourownproxies.sites import *
    account = SexAccount(username='tedwantsmore',password='money1003',email='tedwantsmore@gmx.com')
    account.login()
    board = SexBoard.create(name='test board',description='test board description',account=account)
    print board 
    