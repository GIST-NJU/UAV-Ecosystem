# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-11-21 09:29:20 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-11-21 09:29:20 
"""
import pymysql
from utils import type_dict, order_dict, strtime2datetime, get_reply_tag
from itertools import groupby
from operator import itemgetter

db = pymysql.connect(host='127.0.0.1', user='zzn', password='123456',
                     db='uav_ecosystem', cursorclass=pymysql.cursors.DictCursor)
#ip 119.27.163.222

def get_cursor():
    db.ping(reconnect=True)
    cursor = db.cursor()
    return cursor


def query_user(user_name):
    cursor = get_cursor()
    sql = 'SELECT * FROM user WHERE userId = "{}" OR userName = "{}"'.format(
        user_name, user_name)
    cursor.execute(sql)
    user = cursor.fetchone()
    cursor.close()
    return user


def query_user_by_id(id):
    cursor = get_cursor()
    sql = 'SELECT * FROM user WHERE id = "{}"'.format(id)
    cursor.execute(sql)
    user = cursor.fetchone()
    cursor.close()
    return user


def query_post_by_postid(post_id):
    cursor = get_cursor()
    sql = 'SELECT * FROM post, `user` WHERE post.authorId = `user`.userId AND postId = "{}"'.format(
        post_id)
    cursor.execute(sql)
    post = cursor.fetchone()
    cursor.close()
    return post


def query_post_by_type(post_type, order_type):
    cursor = get_cursor()
    if post_type == 0:
        sql = 'SELECT * FROM post, `user` WHERE post.authorId = `user`.userId '
    else:
        sql = 'SELECT * FROM post, `user` WHERE post.authorId = `user`.userId AND predictedPostType = "{}" '.format(
            type_dict[post_type])
    if order_type == 0:
        sql += 'ORDER BY createTime DESC'
    elif order_type == 1:
        sql += 'ORDER BY replyFlag DESC, lastReplyTime DESC, createTime DESC'
    elif order_type == 2:
        sql += 'ORDER BY lookCnts DESC, lastReplyTime DESC, createTime DESC'
    else:
        sql += 'AND essenceType = 1 ORDER BY lastReplyTime DESC,createTime DESC'
    cursor.execute(sql)
    posts = cursor.fetchall()
    for post in posts:
        post['reply_tag'] = get_reply_tag(post['lastReplyTime'])
    cursor.close()
    return posts


def query_postreply_by_postid(post_id):
    cursor = get_cursor()
    sql = 'SELECT * FROM postreply, `user` WHERE postreply.replyAuthorId = `user`.userId AND postId = "{}" ORDER BY replyTime'.format(
        post_id)
    cursor.execute(sql)
    post_replys = cursor.fetchall()
    cursor.close()
    return post_replys


def query_postreplycomment_by_postid(post_id):
    cursor = get_cursor()
    sql = 'SELECT * FROM postreplycomment, user AS author_user,`user` AS target_user '
    sql += 'WHERE postreplycomment.commentAuthorId = author_user.userId AND postreplycomment.commentTargetAuthorId = target_user.userId AND postId = "{}"'.format(
        post_id)
    cursor.execute(sql)
    post_reply_comments = cursor.fetchall()
    if len(post_reply_comments) == 0:
        return {}
    post_reply_comments.sort(key=itemgetter('postReplyId'))

    groups = groupby(post_reply_comments, key=itemgetter('postReplyId'))
    res = {}
    for key, items in groups:
        res[key] = sorted(list(items), key=itemgetter('commentCreateTime'))
    cursor.close()
    return res


def query_comment_by_commentId(comment_id):
    cursor = get_cursor()
    sql = 'SELECT commentAuthorName,commentAuthorId FROM postreplycomment WHERE commentId = "{}"'.format(
        comment_id)
    cursor.execute(sql)
    comment = cursor.fetchone()
    cursor.close()
    return comment


def query_postreply_by_postreplyid(postreplyid):
    cursor = get_cursor()
    sql = 'SELECT  * FROM postreply, user WHERE postreply.postReplyId = "{}" AND postreply.replyAuthorId = user.userId'.format(
        postreplyid)
    cursor.execute(sql)
    postreply = cursor.fetchone()
    cursor.close()
    return postreply


def query_hot_post():
    cursor = get_cursor()
    sql = 'SELECT postId,title,createTime,lookCnts FROM post ORDER BY lookCnts DESC LIMIT 0,10'
    cursor.execute(sql)
    hot_posts = cursor.fetchall()
    cursor.close()
    return hot_posts


def query_recommended_post():
    cursor = get_cursor()
    sql = 'SELECT postId,title,createTime,lookCnts,id FROM post WHERE id>=(SELECT FLOOR(RAND()*(SELECT MAX(id) FROM post))) LIMIT 10'
    cursor.execute(sql)
    rec_posts = cursor.fetchall()
    cursor.close()
    return rec_posts


def get_recommended_post_by_log(userId):
    cursor = get_cursor()
    sql = 'SELECT postId,lookTime FROM postlooklog WHERE userId = "{}" ORDER BY lookTime DESC'.format(userId)
    cursor.execute(sql)
    looklogs = cursor.fetchall()
    cursor.close()
    postidset = set()
    for looklog in looklogs:
        if looklog['postId'] not in postidset:
            postidset.add(looklog['postId'])
        if len(postidset) ==5:
            break
    lookpostid_list = list(postidset)
    simi_postid_list = []
    for look_postid in lookpostid_list:
        cursor = get_cursor()
        sql = 'SELECT simPosts FROM post WHERE postId = "{}"'.format(look_postid)
        cursor.execute(sql)
        top2_sim_post_id = cursor.fetchone()['simPosts'].split(',')[:2]
        cursor.close()
        simi_postid_list+=top2_sim_post_id
    hot_post_cnts = 10-len(simi_postid_list)
    cursor = get_cursor()
    sql = 'SELECT postId,lookCnts FROM post ORDER BY lookCnts DESC LIMIT 0,{}'.format(hot_post_cnts)
    cursor.execute(sql)
    hot_posts = cursor.fetchall()
    cursor.close()
    for hot_post in hot_posts:
        simi_postid_list.append(hot_post['postId'])
    rec_posts = []
    for sim_post_id in simi_postid_list:
        cursor = get_cursor()
        sql = 'SELECT postId,title,createTime,lookCnts FROM post WHERE postId = "{}"'.format(sim_post_id)
        cursor.execute(sql)
        rec_post = cursor.fetchone()
        cursor.close()
        rec_posts.append(rec_post)
    return rec_posts





def query_simi_post(post_id):
    cursor = get_cursor()
    sql = 'SELECT simPosts FROM post WHERE postId = "{}"'.format(post_id)
    cursor.execute(sql)
    sim_post_id_list = cursor.fetchone()['simPosts'].split(',')[:10]
    cursor.close()
    simi_posts = []
    
    for sim_post_id in sim_post_id_list:
        cursor = get_cursor()
        sql = 'SELECT postId,title,createTime,lookCnts FROM post WHERE postId = "{}"'.format(sim_post_id)
        cursor.execute(sql)
        sim_post = cursor.fetchone()
        simi_posts.append(sim_post)
        cursor.close()
    return simi_posts



def query_post_by_author_id(author_id):
    cursor = get_cursor()
    sql = "SELECT postId,title,createTime FROM post WHERE authorId = '{}' ORDER BY createTime DESC".format(
        author_id)
    cursor.execute(sql)
    posts = cursor.fetchall()
    cursor.close()
    return posts


def query_look_log_by_user_id(user_id):
    cursor = get_cursor()
    sql = "SELECT post.postId, any_value(title), any_value(content), MAX(lookTime) FROM post, postlooklog WHERE "
    sql += "post.postId = postlooklog.postId AND userId = '{}' GROUP BY post.postId ORDER BY MAX(lookTime) DESC".format(
        user_id)
    cursor.execute(sql)
    look_logs = cursor.fetchall()
    cursor.close()
    return look_logs


def query_collection_by_user_id(user_id):
    cursor = get_cursor()
    sql = "SELECT post.postId, title, content, collectedTime, collectedUserId FROM post, postcollection WHERE "
    sql += "post.postId = postcollection.postId AND collectedUserId = '{}' ORDER BY collectedTime DESC".format(
        user_id)
    cursor.execute(sql)
    collections = cursor.fetchall()
    cursor.close()
    return collections


def query_all_papers():
    cursor = get_cursor()
    sql = 'SELECT * FROM uavpapers'
    cursor.execute(sql)
    papers = cursor.fetchall()
    cursor.close()
    return papers

def get_recommended_papers():
    cursor = get_cursor()
    sql = 'SELECT * FROM uavpapers WHERE id>=(SELECT FLOOR(RAND()*(SELECT MAX(id) FROM uavpapers))) LIMIT 10'
    cursor.execute(sql)
    papers = cursor.fetchall()
    cursor.close()
    return papers



def query_post_author(post_id):
    cursor = get_cursor()
    sql = "SELECT authorId,authorName,title FROM post WHERE postId = '{}'".format(
        post_id)
    cursor.execute(sql)
    author = cursor.fetchone()
    cursor.close()
    return author


def query_votecnts(post_id):
    cursor = get_cursor()
    sql = 'SELECT typeVoteCnts FROM post WHERE postId = "{}"'.format(post_id)
    cursor.execute(sql)
    votecnts = cursor.fetchone()
    cursor.close()
    return votecnts


def query_message_by_userid(user_id):
    cursor = get_cursor()
    sql = 'SELECT toUserId FROM message WHERE toUserId = "{}" AND readFlag = 0'.format(
        user_id)
    cursor.execute(sql)
    message = cursor.fetchall()
    cursor.close()
    return len(message)

def query_probas_by_postid(post_id):
    cursor = get_cursor()
    sql = 'SELECT faultProba FROM post WHERE postId = "{}"'.format(post_id)
    cursor.execute(sql)
    proba = cursor.fetchone()
    cursor.close()
    return proba

def query_fmea_dict_by_postid(post_id):
    cursor = get_cursor()
    sql = 'SELECT predictedPostType, faultProba, riskType, entity0, entity1, entity2, entity3, entity4 FROM post WHERE postId = "{}"'.format(post_id)
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    return data



def insert_user(dit):
    cursor = get_cursor()
    sql = "INSERT INTO user (userId, userName, passWord, userIcon, userType, drivingAge) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(
        dit['userid'], dit['username'], dit['password'], dit['userIcon'], dit['userType'], dit['drivingAge'])
    cursor.execute(sql)
    db.commit()
    cursor.close()


def insert_post(dit):
    cursor = get_cursor()
    sql = "INSERT INTO post ("
    key_list = list(dit.keys())
    value_list = ["'{}'".format(value) for value in list(dit.values())]
    sql += ', '.join(key_list)
    sql += ') VALUES ('
    sql += ", ".join(value_list)
    sql += ')'
    cursor.execute(sql)
    cursor.close()
    db.commit()


def insert_post_reply(dit):
    cursor = get_cursor()
    sql = "INSERT INTO postreply ("
    key_list = list(dit.keys())
    value_list = ["'{}'".format(value) for value in list(dit.values())]
    sql += ', '.join(key_list)
    sql += ') VALUES ('
    sql += ", ".join(value_list)
    sql += ')'
    cursor.execute(sql)
    cursor.close()
    db.commit()


def insert_postreply_comment(dit):
    cursor = get_cursor()
    sql = "INSERT INTO postreplycomment ("
    key_list = list(dit.keys())
    value_list = ["'{}'".format(value) for value in list(dit.values())]
    sql += ', '.join(key_list)
    sql += ') VALUES ('
    sql += ", ".join(value_list)
    sql += ')'
    cursor.execute(sql)
    cursor.close()
    db.commit()


def insert_collection_log(dit):
    cursor = get_cursor()
    sql = "INSERT INTO postcollection ("
    key_list = list(dit.keys())
    value_list = ["'{}'".format(value) for value in list(dit.values())]
    sql += ', '.join(key_list)
    sql += ') VALUES ('
    sql += ", ".join(value_list)
    sql += ')'
    cursor.execute(sql)
    cursor.close()
    db.commit()


def insert_like_log(dit):
    cursor = get_cursor()
    sql = "INSERT INTO postlike ("
    key_list = list(dit.keys())
    value_list = ["'{}'".format(value) for value in list(dit.values())]
    sql += ', '.join(key_list)
    sql += ') VALUES ('
    sql += ", ".join(value_list)
    sql += ')'
    cursor.execute(sql)
    cursor.close()
    db.commit()


def insert_hate_log(dit):
    cursor = get_cursor()
    sql = "INSERT INTO posthate ("
    key_list = list(dit.keys())
    value_list = ["'{}'".format(value) for value in list(dit.values())]
    sql += ', '.join(key_list)
    sql += ') VALUES ('
    sql += ", ".join(value_list)
    sql += ')'
    cursor.execute(sql)
    cursor.close()
    db.commit()


def insert_post_look_log(dit):
    cursor = get_cursor()
    sql = "INSERT INTO postlooklog ("
    key_list = list(dit.keys())
    value_list = ["'{}'".format(value) for value in list(dit.values())]
    sql += ', '.join(key_list)
    sql += ') VALUES ('
    sql += ", ".join(value_list)
    sql += ')'
    cursor.execute(sql)
    cursor.close()
    db.commit()


def insert_paper(dit):
    cursor = get_cursor()
    sql = "INSERT INTO uploadpaper ("
    key_list = list(dit.keys())
    value_list = ["'{}'".format(value) for value in list(dit.values())]
    sql += ', '.join(key_list)
    sql += ') VALUES ('
    sql += ", ".join(value_list)
    sql += ')'
    cursor.execute(sql)
    cursor.close()
    db.commit()


def insert_comment_comment(dit):
    pass


def insert_message(dit):
    cursor = get_cursor()
    sql = "INSERT INTO message ("
    key_list = list(dit.keys())
    value_list = ["'{}'".format(value) for value in list(dit.values())]
    sql += ', '.join(key_list)
    sql += ') VALUES ('
    sql += ", ".join(value_list)
    sql += ')'
    cursor.execute(sql)
    cursor.close()
    db.commit()


def update_votecnts(post_id, votecnts):
    cursor = get_cursor()
    sql = 'UPDATE post SET typeVoteCnts = "{}" WHERE postId = "{}"'.format(
        votecnts, post_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def update_reply_cnts(post_id):
    cursor = get_cursor()
    sql = "UPDATE post SET replyCnts = replyCnts + 1, replyFlag = 1 WHERE postId = '{}'".format(
        post_id)
    cursor.execute(sql)
    # print(sql)
    cursor.close()
    db.commit()


def update_look_cnts(post_id):
    cursor = get_cursor()
    sql = "UPDATE post SET lookCnts = lookCnts + 1 WHERE postId = '{}'".format(
        post_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def update_lastReplyTime(post_id, now_time):
    cursor = get_cursor()
    sql = "UPDATE post SET lastReplyTime = '{}' WHERE postId = '{}'".format(
        now_time, post_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def update_commentCnts(post_reply_id):
    cursor = get_cursor()
    sql = "UPDATE postreply SET commentCnts = commentCnts + 1 WHERE postReplyId = '{}'".format(
        post_reply_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def add_update_collectedCnts(post_id):
    cursor = get_cursor()
    sql = "UPDATE post SET collectedCnts = collectedCnts + 1 WHERE postId = '{}'".format(
        post_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def sub_update_collectedCnts(post_id):
    cursor = get_cursor()
    sql = "UPDATE post SET collectedCnts = collectedCnts - 1 WHERE postId = '{}'".format(
        post_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def add_update_likeCnts(post_id):
    cursor = get_cursor()
    sql = "UPDATE post SET likeCnts = likeCnts + 1 WHERE postId = '{}'".format(
        post_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def sub_update_likeCnts(post_id):
    cursor = get_cursor()
    sql = "UPDATE post SET likeCnts = likeCnts - 1 WHERE postId = '{}'".format(
        post_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def add_update_hateCnts(post_id):
    cursor = get_cursor()
    sql = "UPDATE post SET hateCnts = hateCnts + 1 WHERE postId = '{}'".format(
        post_id)
    cursor.execute(sql)
    db.commit()
    cursor.close()


def sub_update_hateCnts(post_id):
    cursor = get_cursor()
    sql = "UPDATE post SET hateCnts = hateCnts - 1 WHERE postId = '{}'".format(
        post_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def is_collected(post_id, user_id):
    cursor = get_cursor()
    sql = "SELECT * FROM postcollection WHERE postId = '{}' AND collectedUserId = '{}'".format(
        post_id, user_id)
    cursor.execute(sql)

    if len(cursor.fetchall()) == 0:
        cursor.close()
        return False
    else:
        cursor.close()
        return True


def is_liked(post_id, user_id):
    cursor = get_cursor()
    sql = "SELECT * FROM postlike WHERE postId = '{}' AND likeUserId = '{}'".format(
        post_id, user_id)
    cursor.execute(sql)
    if len(cursor.fetchall()) == 0:
        cursor.close()
        return False
    else:
        cursor.close()
        return True


def is_hated(post_id, user_id):
    cursor = get_cursor()
    sql = "SELECT * FROM posthate WHERE postId = '{}' AND hateUserId = '{}'".format(
        post_id, user_id)
    cursor.execute(sql)
    if len(cursor.fetchall()) == 0:
        cursor.close()
        return False
    else:
        cursor.close()
        return True


def is_reply_liked(post_id, post_reply_id, user_id):
    cursor = get_cursor()
    sql = "SELECT * FROM postreplylike WHERE postId = '{}' AND postReplyId = '{}' AND postReplyLikeUserId = '{}'".format(
        post_id, post_reply_id, user_id)
    cursor.execute(sql)
    if len(cursor.fetchall()) == 0:
        cursor.close()
        return False
    else:
        cursor.close()
        return True


def is_new_userid(user_id):
    cursor = get_cursor()
    sql = "SELECT userId FROM user WHERE userId = '{}'".format(user_id)
    cursor.execute(sql)
    if len(cursor.fetchall()) == 0:
        cursor.close()
        return True
    else:
        cursor.close()
        return False


def is_new_username(user_name):
    cursor = get_cursor()
    sql = "SELECT userName FROM user WHERE userName = '{}'".format(user_name)
    cursor.execute(sql)
    if len(cursor.fetchall()) == 0:
        cursor.close()
        return True
    else:
        cursor.close()
        return False


def delete_post_by_post_id(post_id):
    cursor = get_cursor()
    sql = "DELETE FROM post WHERE postId = '{}'".format(post_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def delete_collection_log(post_id, user_id):
    cursor = get_cursor()
    sql = "DELETE FROM postcollection WHERE postId = '{}' AND collectedUserId = '{}'".format(
        post_id, user_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def delete_like_log(post_id, user_id):
    cursor = get_cursor()
    sql = "DELETE FROM postlike WHERE postId = '{}' AND likeUserId = '{}'".format(
        post_id, user_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def delete_hate_log(post_id, user_id):
    cursor = get_cursor()
    sql = "DELETE FROM posthate WHERE postId = '{}' AND hateUserId = '{}'".format(
        post_id, user_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def insert_reply_like_log(dit):
    cursor = get_cursor()
    sql = "INSERT INTO postreplylike ("
    key_list = list(dit.keys())
    value_list = ["'{}'".format(value) for value in list(dit.values())]
    sql += ', '.join(key_list)
    sql += ') VALUES ('
    sql += ", ".join(value_list)
    sql += ')'
    cursor.execute(sql)
    cursor.close()
    db.commit()


def delete_reply_like_log(post_id, post_reply_id, user_id):
    cursor = get_cursor()
    sql = "DELETE FROM postreplylike WHERE postId = '{}' AND postReplyId = '{}' AND postReplyLikeUserId = '{}'".format(
        post_id, post_reply_id, user_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def sub_update_postreply_likeCnts(post_id, post_reply_id):
    cursor = get_cursor()
    sql = "UPDATE postreply SET likeCnts = likeCnts - 1 WHERE postId = '{}' AND postReplyId = '{}'".format(
        post_id, post_reply_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


def add_update_postreply_likeCnts(post_id, post_reply_id):
    cursor = get_cursor()
    sql = "UPDATE postreply SET likeCnts = likeCnts + 1 WHERE postId = '{}' AND postReplyId = '{}'".format(
        post_id, post_reply_id)
    cursor.execute(sql)
    cursor.close()
    db.commit()


if __name__ == '__main__':
    query_post_by_type(0, 0)
