# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-12-02 09:57:47 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-12-02 09:57:47 
"""
import datetime
type_dict = {
    0: '全部',
    1: 'Bias',
    2: 'Drift',
    3: 'Performance degradation',
    4: 'Freezing',
    5: 'Calibration error',
    6: 'Lock in place',
    7: 'Float',
    8: 'Hard over',
    9: 'Loss of Effectiveness',
    10: '失误操作',
    11: '电池故障',
    12: '信号干扰',
    13: '避障失效',
    14: '返航故障',
    15: '其他'
}
order_dict = {
    0: '最新发布',
    1: '最新回复',
    2: '最热',
    3: '精华'
}


def strtime2datetime(strtime):
    date, time = strtime.split(' ')
    year, month, day = map(int, date.split('-'))
    hour, minute, second = map(int, time.split(':'))
    return datetime.datetime(year, month, day, hour, minute, second)


def get_reply_tag(reply_strtime):
    if reply_strtime == '':
        return ''
    reply_time = strtime2datetime(reply_strtime)
    now = datetime.datetime.now()
    time_delta = now-reply_time
    timedelta_days = time_delta.days
    timedelta_seconds = time_delta.seconds
    if timedelta_days > 0 and timedelta_days < 31:
        reply_tag = '{}天前回复'.format(timedelta_days)
    elif timedelta_days >= 31 and timedelta_days < 365:
        reply_tag = '{}个月前回复'.format(timedelta_days//30)
    elif timedelta_days >= 366:
        reply_tag = '{}年前回复'.format(timedelta_days//365)
    else:  # timedelta_days = 0
        if timedelta_seconds < 60:
            reply_tag = '刚刚回复'
        elif timedelta_seconds >= 60 and timedelta_seconds < 3600:
            reply_tag = '{}分钟前回复'.format(timedelta_seconds//60)
        else:  # timedelta_seconds>=3600
            reply_tag = '{}小时前回复'.format(timedelta_seconds//3600)
    return reply_tag
