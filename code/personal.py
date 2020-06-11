# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-12-02 15:58:46 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-12-02 15:58:46 
"""
from flask import Blueprint, render_template, session, request, redirect
from flask_login import login_required, current_user
from mysql import query_user_by_id, query_post_by_author_id, delete_post_by_post_id, query_look_log_by_user_id, query_collection_by_user_id
from flask_paginate import Pagination, get_page_parameter

personal_app = Blueprint('personal_app', __name__)


@personal_app.route('/user/<user_id>/<log_id>', methods=['GET', 'POST'])
@login_required
def personal(user_id, log_id):
    if request.method == 'GET':
        session['redirect'] = '/'
    css_dict = {0: '', 1: '', 2: '', 3: ''}
    css_dict[int(log_id)] = 'active'
    look_user = query_user_by_id(int(user_id))
    look_user_user_id = look_user['userId']
    current_user_user_id = current_user.get_id()
    current_user_flag = look_user_user_id == current_user_user_id
    if log_id == '0':
        data = query_post_by_author_id(look_user_user_id)
        # print(data)
    elif log_id == '1':
        data = query_look_log_by_user_id(current_user_user_id)
        # print(data)
    elif log_id == '2':
        data = []
    else:
        data = query_collection_by_user_id(current_user_user_id)
    perpage = 10
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=len(
        data), record_name='users', bs_version=4, prev_label='上一页', next_label='下一页', alignment='center', per_page=perpage)
    start = (page-1)*perpage
    end = start+perpage
    return render_template('personal.html', look_user=look_user, log_id=int(log_id),
                           css_dict=css_dict, current_user_flag=current_user_flag,
                           data=data[start:end], pagination=pagination
                           )


@personal_app.route('/delete_post/<post_id>', methods=['GET'])
def delete_post(post_id):
    current_user_uid = current_user.user_uid
    delete_post_by_post_id(post_id)
    return redirect('/user/{}/0'.format(current_user_uid))
