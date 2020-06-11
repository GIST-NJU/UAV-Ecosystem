# -*- coding: utf-8 -*-
"""
  @Author: zzn
  @Date: 2019-12-18 12:06:25
  @Last Modified by:   zzn
  @Last Modified time: 2019-12-18 12:06:25
"""

from flask import Blueprint, render_template, request, session, jsonify
from autofmea import get_test_vec,idx2label,predict_fault,get_predict_entity_list,predict_risk,predict_fault_proba
import requests
import json
import numpy as np


api_app = Blueprint('api_app', __name__)


@api_app.route('/api', methods=['GET'])
def api():
    session['redirect'] = request.path
    return render_template('api.html')


@api_app.route('/api/diagnosis', methods=['POST'])
def diagnosis():
	texts = json.loads(request.data)
	test_vecs = get_test_vec(texts)
	predicted_faults = predict_fault(test_vecs)
	return jsonify(predicted_faults)


@api_app.route('/api/fmea',methods=['POST'])
def fmea():
	texts = json.loads(request.data)
	test_vecs = get_test_vec(texts)
	predicted_faults = predict_fault(test_vecs)
	risks = predict_risk(test_vecs)
	entity_dicts = get_predict_entity_list(texts)
	probas = predict_fault_proba(test_vecs)
	fmea_dicts = []
	for i,fault_mode in enumerate(predicted_faults):
		fmea_dict = {}
		fmea_dict['故障模式'] = fault_mode
		fmea_dict['发生概率'] = np.max(probas[i])
		fmea_dict['风险系数'] = risks[i]
		fmea_dict['无人机型号'] = entity_dicts[i][0]
		fmea_dict['发生环境'] = entity_dicts[i][1]
		fmea_dict['人行为'] = entity_dicts[i][2]
		fmea_dict['无人机行为'] = entity_dicts[i][3]
		fmea_dict['损坏情况'] = entity_dicts[i][4]
		fmea_dicts.append(fmea_dict)
	return jsonify(fmea_dicts)
