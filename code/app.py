# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-11-19 16:14:05 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-11-19 16:14:05 
"""
import os
import flask
from flask import render_template, redirect, session, request, jsonify
from flask_login import (LoginManager, UserMixin, current_user,
                         fresh_login_required, login_required, login_user,
                         logout_user)
from login import login_app
from register import reg_app
from bbs import bbs_app
from personal import personal_app
from publish_post import publish_post_app
from post_details import post_app
from paper import paper_app
from diagnosis import diagnosis_app
from api import api_app
from mysql import query_user, query_message_by_userid
from user import User
from search import search_app

app = flask.Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Unauthorized User'
login_manager.login_message_category = "info"


# 注册蓝图

app.register_blueprint(login_app)
app.register_blueprint(reg_app)
app.register_blueprint(bbs_app)
app.register_blueprint(personal_app)
app.register_blueprint(publish_post_app)
app.register_blueprint(post_app)
app.register_blueprint(paper_app)
app.register_blueprint(diagnosis_app)
app.register_blueprint(api_app)
app.register_blueprint(search_app)

@login_manager.user_loader
def load_user(user_name):
    user = query_user(user_name)
    if user is not None:
        curr_user = User(user['userId'], user['userName'],
                         user['passWord'], user['userIcon'], user['id'])
        return curr_user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect('login')


@app.route('/')
def index():
    print(request.headers.get('X-Real-Ip'))
    if current_user.is_active:
        print(current_user.get_id(), current_user.name)
    return render_template('index.html')


@app.route('/get_message_count', methods=['GET'])
def get_message_count():
    user_id = request.args.get('user_id')
    print(user_id)
    msg_cnts = query_message_by_userid(user_id)
    print(msg_cnts)
    return jsonify(msg_cnts)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, threaded=True)
