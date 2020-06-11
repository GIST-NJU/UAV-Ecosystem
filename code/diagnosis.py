# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-12-18 12:03:30 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-12-18 12:03:30 
"""

import numpy as np
from flask import Blueprint, render_template, request, session
from autofmea import get_test_vec,idx2label,predict_fault_proba,get_predict_entity_list,predict_risk
diagnosis_app = Blueprint('diagnosis_app', __name__)


@diagnosis_app.route('/diagnosis', methods=['GET', 'POST'])
def diagnosis():
    session['redirect'] = request.path
    if request.method == 'GET':
        diagnosis_text = '好吧，我承认操作失误撞玻璃上了！70多米坠落，竟然没有四分五裂，只是电池飞了，断了骨头连着筋！才买了不到半年啊 崭新崭新的AIR.但是，我有DJI care保驾护航。寄送当天大疆就回寄了，效率点赞！不知道是否是新机，客服说是符合出厂标准的合格机。新机所有设置重新开过，开始飞了！新手建议购买DJI care ！'
    else:
        diagnosis_text = request.form.get('content')

    test_vec = get_test_vec([diagnosis_text])
    probas = predict_fault_proba(test_vec)[0]
    data = []
    for i, proba in enumerate(probas):
        cur_item = {}
        cur_item['value'] = proba
        cur_item['name'] = idx2label[i]
        data.append(cur_item)
    max_proba_label = np.argmax(probas)
    data[max_proba_label]['selected'] = 'true'

    risk = predict_risk(test_vec)[0]
    entity_dict = get_predict_entity_list([diagnosis_text])[0]
    print(entity_dict)
    fmea_dict = {}
    fmea_dict['fault_mode'] = idx2label[max_proba_label]
    fmea_dict['proba'] = '{:.4f}'.format(np.max(probas))
    fmea_dict['risk'] = risk
    fmea_dict.update(entity_dict)
    for key in fmea_dict:
        if fmea_dict[key] == '':
            fmea_dict[key] = '/'
    return render_template('fault_diagnosis.html', diagnosis_text=diagnosis_text,fmea_dict=fmea_dict, data=data)
