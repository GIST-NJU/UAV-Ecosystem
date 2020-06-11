# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-11-19 21:15:17 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-11-19 21:15:17 
"""
from flask import Blueprint, request, redirect, render_template, url_for, flash, session

from flask_login import (LoginManager, UserMixin, current_user,
                         fresh_login_required, login_required, login_user,
                         logout_user)

from mysql import query_user

from user import User
login_app = Blueprint('login_app', __name__)


@login_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        user_dit = query_user(username)
        if user_dit is not None and request.form['password'] == user_dit['passWord']:
            cur_user = User(user_dit['userId'],
                            user_dit['userName'], user_dit['passWord'], user_dit['userIcon'], user_dit['id'])
            cur_user.username = username
            login_user(cur_user)

            #next_ = request.args.get('next')
            # print(request.args.get('next'))
            session['username'] = user_dit['userName']
            res = session.get('redirect')
            if res:
                return redirect(res)
            return redirect(url_for('index'))
        flash('用户名或密码错误!')
    return render_template('login.html')


@login_app.route('/logout')
@login_required
def logout():
    logout_user()
    res = session.get('redirect')
    if res:
        return redirect(res)
    return redirect(url_for('index'))
