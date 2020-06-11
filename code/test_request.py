# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-12-29 11:32:31 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-12-29 11:32:31 
"""
import json
import requests

CLASSIFY_URL = 'http://uavecosystem.cn/api/diagnosis'

s = [
    "好吧，我承认操作失误撞玻璃上了！70多米坠落，竟然没有四分五裂，只是电池飞了，断了骨头连着筋！才买了不到半年啊 崭新崭新的AIR啊",
    "某天下午玩，那时地面一点风也没有，拉高到500米，正准备拍云，突然提示风速过大，然后姿态球乱飘，一转眼飞飞机飘了300米，因为有干扰，所以失联了，我迅速往飞机那个方向跑，结果连上信号了以后飞机已经被风刮到一个两公里外的荒山沟里去了，还有百分之14的电，那么大的风开了运动档也飞不动了，最后迫降到了山里……提醒飞友，提示风速过大一定要注意"
]

data = json.dumps(s)
headers = {
    'X-Token': 'YOUR_API_TOKEN',
    'Content-Type': 'application/json'
}
resp = requests.post(CLASSIFY_URL, headers=headers, data=data.encode('utf-8'))
print(resp.text)
