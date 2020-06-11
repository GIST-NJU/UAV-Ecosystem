# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-11-21 13:14:31 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-11-21 13:14:31 
"""
import random
from flask import request, render_template, Blueprint, redirect
from mysql import insert_user, is_new_userid, is_new_username
from sendemail import send_register_email
reg_app = Blueprint('reg_app', __name__)


@reg_app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        dit = request.form.to_dict()
        print(dit)
        dit['userIcon'] = '/static/imgs/{}.png'.format(random.randint(1, 26))
        insert_user(dit)
        send_register_email(dit['userid'])
        return redirect('login')
    return render_template('register.html')


@reg_app.route('/register/userid_valid', methods=['GET', 'POST'])
def valid_userid():
    if request.method == 'GET':
        return render_template('userid_valid.html', flag=True)
    else:
        user_id = request.form.get('userid')
        if is_new_userid(user_id):
            return render_template('userid_valid.html', flag=True)
        else:
            return render_template('userid_valid.html', flag=False)


@reg_app.route('/register/username_valid', methods=['GET', 'POST'])
def valid_username():
    if request.method == 'GET':
        return render_template('username_valid.html', flag=True)
    else:
        user_name = request.form.get('username')
        if is_new_username(user_name):
            return render_template('username_valid.html', flag=True)
        else:
            return render_template('username_valid.html', flag=False)
