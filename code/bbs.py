# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-11-26 15:05:44 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-11-26 15:05:44 
"""
from flask import Blueprint, request, redirect, render_template, url_for, flash, session

from flask_login import (LoginManager, UserMixin, current_user,
                         fresh_login_required, login_required, login_user,
                         logout_user)

from flask_paginate import Pagination, get_page_parameter
from mysql import query_user, query_post_by_type, query_hot_post, query_recommended_post,get_recommended_post_by_log
from user import User
from utils import type_dict, order_dict

bbs_app = Blueprint('bbs_app', __name__)


@bbs_app.route('/bbs/', methods=['GET', 'POST'])
def get_bbs():
    session['redirect'] = request.path
    try:
        type, order = int(request.args['type']), int(request.args['order'])
    except:
        type, order = 0, 0
    type_text = {v: '' for k, v in type_dict.items()}
    type_text[type_dict[type]] = 'active'
    order_text = {v: '' for k, v in order_dict.items()}
    order_text[order_dict[order]] = 'active'
    posts = query_post_by_type(type, order)
    perpage = 20
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=len(
        posts), record_name='users', bs_version=4, prev_label='上一页', next_label='下一页', alignment='center', per_page=perpage)
    start = (page-1)*perpage
    end = start+perpage

    hot_posts = query_hot_post()

    if current_user.get_id() is None:
        print('not')
        rec_posts = query_recommended_post()
    else:
        print('yes')
        current_user_info = query_user(current_user.get_id())
        userId = current_user_info['userId']
        
        rec_posts = get_recommended_post_by_log(userId)

    return render_template(
        'bbs.html', type_text=type_text,
        order_text=order_text, data=posts[start:end],
        pagination=pagination, hot_posts=hot_posts,
        rec_posts=rec_posts
    )


if __name__ == '__main__':
    pass
