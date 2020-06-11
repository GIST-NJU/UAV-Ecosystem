# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-12-05 16:42:48 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-12-05 16:42:48 
"""
import pymysql
from itertools import groupby
from operator import itemgetter


if __name__ == '__main__':

    db = pymysql.connect(host='127.0.0.1', user='zzn', password='123456',
                         db='uav_ecosystem', cursorclass=pymysql.cursors.DictCursor)

    def get_cursor():
        db.ping(reconnect=True)
        cursor = db.cursor()
        return cursor

    def update_user(user_id):
        cursor = get_cursor()
        sql = 'UPDATE user SET userId = "{}" WHERE userId = "{}"'.format(
            user_id.replace('qq.com', 'uavecosystem.cn'), user_id)
        cursor.execute(sql)
        # print(sql)
        cursor.close()
        db.commit()

    def update_post(user_id):
        cursor = get_cursor()
        sql = 'UPDATE post SET authorId = "{}" WHERE authorId = "{}"'.format(
            user_id.replace('qq.com', 'uavecosystem.cn'), user_id)
        cursor.execute(sql)
        # print(sql)
        cursor.close()
        db.commit()

    cursor = get_cursor()

