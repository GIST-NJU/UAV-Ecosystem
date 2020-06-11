# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-12-03 16:03:07 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-12-03 16:03:07 
"""
import uuid
from flask import Blueprint, request, render_template, session, redirect, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from mysql import query_user, insert_post
from bs4 import BeautifulSoup
from autofmea import get_predict_entity_list,get_test_vec,predict_fault,predict_fault_proba,predict_risk
publish_post_app = Blueprint('publish_post_app', __name__,)


@publish_post_app.route('/publish_post', methods=['GET', 'POST'])
@login_required
def publish_post():
    if request.method == 'GET':
        return render_template('publish_post.html')
    else:  # request.method = 'POST'
        dit = request.form.to_dict()
        now_time = str(datetime.now())[:19]
        dit['createTime'] = now_time
        dit['lastReplyTime'] = ''
        post_id = str(uuid.uuid1()).replace('-', '')
        dit['postId'] = post_id
        current_user_info = query_user(current_user.get_id())
        dit['authorId'] = current_user_info['userId']
        dit['authorName'] = current_user_info['userName']
        dit['likeCnts'] = 0
        dit['hateCnts'] = 0
        dit['replyCnts'] = 0
        dit['lookCnts'] = 0
        dit['replyFlag'] = 0
        dit['collectedCnts'] = 0
        content_html = dit['contentHtml']
        soup = BeautifulSoup(content_html, 'html.parser')
        content = soup.text
        dit['content'] = content
        dit['typeVoteCnts'] = '1,1,1,1,1,1,1,1,1,1,1,1,1,1,1'
        entity_list = get_predict_entity_list([content])[0]
        test_vecs = get_test_vec([content])
        fault_probas = predict_fault_proba(test_vecs)[0]
        fault = predict_fault(test_vecs)[0]
        risk = predict_risk(test_vecs)[0]
        for i,key in  enumerate(entity_list):
            dit['entity{}'.format(i)] = entity_list[key]
        dit['predictedPostType'] = fault
        dit['riskType'] = risk
        dit['faultProba'] = ','.join(map(str,fault_probas))
        insert_post(dit)
        return redirect('bbs')


@publish_post_app.route('/publish_post_img', methods=['POST'])
@login_required
def publish_post_img():
    img_files = request.files.getlist('file')
    img_id = str(uuid.uuid1()).replace('-', '')
    img_json = {
        "errno": 0,
        "data": [
        ]
    }
    for i, img_file in enumerate(img_files):
        cur_name = '{}_{}.jpg'.format(img_id, i)
        save_path = 'static/imgs/'+cur_name
        img_file.save(save_path)
        img_json['data'].append('/'+save_path)
    return jsonify(img_json)


if __name__ == '__main__':
    pass
