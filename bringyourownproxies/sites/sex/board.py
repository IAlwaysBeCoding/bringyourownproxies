#!/usr/bin/python
# -*- coding: utf-8 -*-

class SexBoard(object):
    
    def __init__(self,name,board_id,**kwargs):
        self.name = name
        self.board_id = board_id
        super(SexBoard,self).__init__(**kwargs)

def create_board():
    pass