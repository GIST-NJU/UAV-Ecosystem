# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-12-02 14:51:04 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-12-02 14:51:04 
"""
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, name, pass_word, user_icon, user_uid):
        self.id = id
        self.name = name
        self.pass_word = pass_word
        self.user_icon = user_icon
        self.user_uid = user_uid

    def get_id(self):
        return self.id
