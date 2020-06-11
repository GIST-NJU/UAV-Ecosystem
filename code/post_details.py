# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-12-04 13:12:51 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-12-04 13:12:51 
"""
import uuid
import json
from datetime import datetime

from bs4 import BeautifulSoup
from flask import (Blueprint, jsonify, redirect, render_template, request,
                   session)
from flask_login import current_user, login_required

from mysql import (insert_post_reply, query_post_by_postid, insert_post_look_log,
                   query_postreply_by_postid, update_lastReplyTime,
                   update_look_cnts, update_reply_cnts, query_simi_post,
                   query_postreplycomment_by_postid, query_postreply_by_postreplyid,
                   insert_postreply_comment, update_commentCnts,
                   query_comment_by_commentId, is_collected,
                   insert_collection_log, delete_collection_log,
                   add_update_collectedCnts, sub_update_collectedCnts,
                   is_liked, is_hated,
                   add_update_likeCnts, sub_update_likeCnts,
                   add_update_hateCnts, sub_update_hateCnts,
                   insert_like_log, delete_like_log,
                   insert_hate_log, delete_hate_log,
                   is_reply_liked, insert_reply_like_log,
                   delete_reply_like_log, add_update_postreply_likeCnts, sub_update_postreply_likeCnts,
                   insert_message, query_post_author,
                   query_votecnts, update_votecnts,
                   query_probas_by_postid,query_fmea_dict_by_postid,
                   get_recommended_papers)


from sendemail import send_postreply_email
import numpy as np
from autofmea import idx2label,predict_risk,get_predict_entity_list
post_app = Blueprint('post_app', __name__)


@post_app.route('/post/<post_id>', methods=['GET'])
def get_post(post_id):
    '''请求帖子
    '''

    session['redirect'] = request.path
    update_look_cnts(post_id)

    # insert look log table
    look_dit = {}
    look_dit['postId'] = post_id
    if current_user.is_active:
        look_dit['userId'] = current_user.get_id()
    else:
        look_dit['userId'] = '未登录的用户'
    look_dit['lookTime'] = str(datetime.now())[:19]
    look_dit['userAdress'] = request.headers.get('X-Real-Ip')
    insert_post_look_log(look_dit)

    post = query_post_by_postid(post_id)
    post['have_reply'] = post['replyCnts'] != 0
    # print(post)
    post_replys = query_postreply_by_postid(post_id)

    for post_reply in post_replys:
        if current_user.is_active:
            post_reply['postreplyflag'] = is_reply_liked(
                post_id, post_reply['postReplyId'], current_user.get_id())
        else:
            post_reply['postreplyflag'] = False
    comments = query_postreplycomment_by_postid(post_id)
    # print(comments)
    if current_user.is_active:
        post_collected_flag = is_collected(post_id, current_user.get_id())
        post_like_flag = is_liked(post_id, current_user.get_id())
        post_hate_flag = is_hated(post_id, current_user.get_id())
    else:
        post_collected_flag = False
        post_like_flag = False
        post_hate_flag = False
    simi_posts = query_simi_post(post_id)
    # print(post_replys)
    probas = list(map(float,query_probas_by_postid(post_id)['faultProba'].split(',')))
    data = []
    for i, proba in enumerate(probas):
        cur_item = {}
        cur_item['value'] = proba
        cur_item['name'] = idx2label[i]
        data.append(cur_item)
    max_proba_label = np.argmax(probas)
    data[max_proba_label]['selected'] = 'true'
    fmea_data = query_fmea_dict_by_postid(post_id)
    fmea_dict = {}
    fmea_dict['fault_mode'] = fmea_data['predictedPostType']
    fmea_dict['proba'] = '{:.4f}'.format(np.max(probas))
    fmea_dict['risk'] = fmea_data['riskType']
    for i in range(5):
        fmea_dict[i] = fmea_data['entity{}'.format(i)]
    for key in fmea_dict:
        if fmea_dict[key] == '':
            fmea_dict[key] = '/'

    votecnts = list(map(int, query_votecnts(
        post_id)['typeVoteCnts'].split(',')))
    votecnts_data = []
    for i, cnt in enumerate(votecnts):
        cur_item = {}
        cur_item['value'] = cnt
        cur_item['name'] = idx2label[i]
        votecnts_data.append(cur_item)
    max_cnt_label = np.argmax(votecnts)
    votecnts_data[max_cnt_label]['selected'] = 'true'

    papers = get_recommended_papers()

    return render_template('post_details.html', post=post,
                           post_replys=post_replys, simi_posts=simi_posts,
                           comments=comments, post_collected_flag=post_collected_flag,
                           post_like_flag=post_like_flag, post_hate_flag=post_hate_flag,
                           data=data, votecnts_data=votecnts_data,fmea_dict = fmea_dict,papers = papers)


@post_app.route('/typeVote/<post_id>/<type_id>', methods=['POST'])
@login_required
def vote_post(post_id, type_id):

    votecnts = list(map(int, query_votecnts(
        post_id)['typeVoteCnts'].split(',')))
    votecnts[int(type_id)] += 1
    cnts_str = ','.join(map(str, votecnts))
    update_votecnts(post_id, cnts_str)

    votecnts = list(map(int, query_votecnts(
        post_id)['typeVoteCnts'].split(',')))

    votecnts_data = []
    for i, cnt in enumerate(votecnts):
        cur_item = {}
        cur_item['value'] = cnt
        cur_item['name'] = idx2label[i]
        votecnts_data.append(cur_item)
    max_cnt_label = np.argmax(votecnts)
    votecnts_data[max_cnt_label]['selected'] = 'true'
    return render_template('vote_chart_content.html', votecnts_data=votecnts_data)


@post_app.route('/replypost/<post_id>', methods=['POST'])
@login_required
def reply_post(post_id):
    '''回帖
    '''
    dit = request.form.to_dict()
    now_time = str(datetime.now())[:19]
    dit['postReplyId'] = str(uuid.uuid1()).replace('-', '')
    dit['postId'] = post_id
    dit['replyTime'] = now_time
    dit['replyAuthorId'] = current_user.get_id()
    dit['commentCnts'] = 0
    dit['likeCnts'] = 0
    contentHtml = dit['replyContentHtml']
    soup = BeautifulSoup(contentHtml, 'html.parser')
    dit['replyContent'] = soup.text
    insert_post_reply(dit)
    update_reply_cnts(post_id)
    update_lastReplyTime(post_id, now_time)

    message_dict = {}
    message_dict['fromUserId'] = current_user.get_id()
    message_dict['fromUserName'] = current_user.name
    post_author = query_post_author(post_id)
    message_dict['toUserId'] = post_author['authorId']
    message_dict['toUserName'] = post_author['authorName']
    message_dict['messageType'] = '回帖'
    message_dict['messageContent'] = contentHtml
    message_dict['messageCreateTime'] = now_time
    message_dict['readFlag'] = 0
    insert_message(message_dict)
    send_postreply_email(
        current_user.name, post_author['authorName'], post_author['authorId'], post_author['title'], contentHtml)
    return redirect('/post/{}'.format(post_id))


@post_app.route('/upload_reply_post_img', methods=['POST'])
def upload_reply_post_img():
    '''回帖图片的上传
    '''
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


@post_app.route('/replyComment/<post_id>-<post_reply_id>-<comment_id>', methods=['POST'])
@login_required
def reply_comment(post_id, post_reply_id, comment_id):
    '''回复回帖的回复
    '''
    replycontent = request.form.get('replycommentContent')
    comments = query_postreplycomment_by_postid(post_id)
    post_reply = query_postreply_by_postreplyid(post_reply_id)
    # print(data)
    dit = {}
    dit['commentId'] = str(uuid.uuid1()).replace('-', '')
    dit['postReplyId'] = post_reply_id
    dit['postId'] = post_id
    dit['replyAuthorId'] = post_reply['replyAuthorId']
    dit['replyAuthorName'] = post_reply['userName']
    dit['commentAuthorId'] = current_user.get_id()
    dit['commentAuthorName'] = current_user.name

    comment = query_comment_by_commentId(comment_id)
    dit['commentTargetAuthorId'] = comment['commentAuthorId']
    dit['commentTargetAuthorName'] = comment['commentAuthorName']
    dit['commentCreateTime'] = str(datetime.now())[:19]
    dit['commentContent'] = replycontent
    insert_postreply_comment(dit)
    update_commentCnts(post_reply_id)
    comments = query_postreplycomment_by_postid(post_id)
    post_reply = query_postreply_by_postreplyid(post_reply_id)
    post = query_post_by_postid(post_id)
    return render_template('comment_list.html', comments=comments, post_reply=post_reply, post=post)


@post_app.route('/replyPostReply/<post_id>-<post_reply_id>', methods=['POST'])
@login_required
def reply_post_reply(post_id, post_reply_id):
    '''回复回帖
    '''
    replycontent = request.form.get('commentContent')
    # print(replycontent)
    post_reply = query_postreply_by_postreplyid(post_reply_id)
    # print(data)
    dit = {}
    dit['commentId'] = str(uuid.uuid1()).replace('-', '')
    dit['postReplyId'] = post_reply_id
    dit['postId'] = post_id
    dit['replyAuthorId'] = post_reply['replyAuthorId']
    dit['replyAuthorName'] = post_reply['userName']
    dit['commentAuthorId'] = current_user.get_id()
    dit['commentAuthorName'] = current_user.name
    dit['commentTargetAuthorId'] = post_reply['replyAuthorId']
    dit['commentTargetAuthorName'] = post_reply['userName']
    dit['commentCreateTime'] = str(datetime.now())[:19]
    dit['commentContent'] = replycontent
    insert_postreply_comment(dit)
    update_commentCnts(post_reply_id)
    comments = query_postreplycomment_by_postid(post_id)
    post_reply = query_postreply_by_postreplyid(post_reply_id)
    post = query_post_by_postid(post_id)
    return render_template('comment_list.html', comments=comments, post_reply=post_reply, post=post)


@post_app.route('/collect_post/<post_id>', methods=['POST'])
def collect_post(post_id):
    collected_flag = is_collected(post_id, current_user.get_id())
    if collected_flag:
        delete_collection_log(post_id, current_user.get_id())
        sub_update_collectedCnts(post_id)
        return render_template('collection_content.html', post_id=post_id, post_collected_flag=False)
    else:
        dit = {}
        dit['postId'] = post_id
        dit['collectedUserId'] = current_user.get_id()
        dit['collectedTime'] = str(datetime.now())[:19]
        insert_collection_log(dit)
        add_update_collectedCnts(post_id)
        return render_template('collection_content.html', post_id=post_id, post_collected_flag=True)


@post_app.route('/like_post/<post_id>', methods=['POST'])
def like_post(post_id):
    liked_flag = is_liked(post_id, current_user.get_id())
    if liked_flag:
        delete_like_log(post_id, current_user.get_id())
        sub_update_likeCnts(post_id)
        return render_template('like_content.html', post_id=post_id, post_like_flag=False)
    else:
        dit = {}
        dit['postId'] = post_id
        dit['likeUserId'] = current_user.get_id()
        dit['likeTime'] = str(datetime.now())[:19]
        insert_like_log(dit)
        add_update_likeCnts(post_id)
        return render_template('like_content.html', post_id=post_id, post_like_flag=True)


@post_app.route('/hate_post/<post_id>', methods=['POST'])
def hate_post(post_id):
    hated_flag = is_hated(post_id, current_user.get_id())
    if hated_flag:
        delete_hate_log(post_id, current_user.get_id())
        sub_update_hateCnts(post_id)
        return render_template('hate_content.html', post_id=post_id, post_hate_flag=False)
    else:
        dit = {}
        dit['postId'] = post_id
        dit['hateUserId'] = current_user.get_id()
        dit['hateTime'] = str(datetime.now())[:19]
        insert_hate_log(dit)
        add_update_hateCnts(post_id)
        return render_template('hate_content.html', post_id=post_id, post_hate_flag=True)


@post_app.route('/like_post_reply/<post_id>-<post_reply_id>', methods=['POST'])
def like_post_reply(post_id, post_reply_id):
    post_reply_like_flag = is_reply_liked(
        post_id, post_reply_id, current_user.get_id())
    if post_reply_like_flag:
        delete_reply_like_log(post_id, post_reply_id, current_user.get_id())
        sub_update_postreply_likeCnts(post_id, post_reply_id)
        post_reply = query_postreply_by_postreplyid(post_reply_id)
        return render_template('like_postreply_content.html', post_reply_like_flag=False, likeCnts=post_reply['likeCnts'])
    else:
        dit = {}
        dit['postId'] = post_id
        dit['postReplyId'] = post_reply_id
        dit['postReplyLikeUserId'] = current_user.get_id()
        dit['posReplyLikeTime'] = str(datetime.now())[:19]
        insert_reply_like_log(dit)
        add_update_postreply_likeCnts(post_id, post_reply_id)
        post_reply = query_postreply_by_postreplyid(post_reply_id)
        return render_template('like_postreply_content.html', post_reply_like_flag=True, likeCnts=post_reply['likeCnts'])


if __name__ == '__main__':
    pass
