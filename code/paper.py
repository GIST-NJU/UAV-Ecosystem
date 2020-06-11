# -*- coding: utf-8 -*-
"""
  @Author: zzn 
  @Date: 2019-12-17 13:50:36 
  @Last Modified by:   zzn 
  @Last Modified time: 2019-12-17 13:50:36 
"""
from flask import Blueprint, render_template, request, session, redirect
from flask_paginate import Pagination, get_page_parameter
from mysql import query_all_papers, insert_paper
from collections import Counter
paper_app = Blueprint('paper_app', __name__)


@paper_app.route('/papers', methods=['GET'])
def get_papers():
    session['redirect'] = request.path
    papers = query_all_papers()
    perpage = 20
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=len(
        papers), record_name='users', bs_version=4, prev_label='上一页', next_label='下一页', alignment='center', per_page=perpage)
    start = (page-1)*perpage
    end = start+perpage

    years = Counter()
    keywords = Counter()
    for paper in papers:
        year = int(paper['year'])
        years.update([year])
        keyword_list = paper['keywords'].lower().replace(';', ',').split(',')
        keywords.update(keyword_list)
    years = sorted(years.items())
    keywords = {w: c for w, c in keywords.items() if c >= 2}
    visual_data = {}
    visual_data['years'] = [item[0] for item in years]
    visual_data['paperYearCnt'] = [item[1] for item in years]
    visual_data['keywords'] = dict(keywords)
    return render_template('paper.html', pagination=pagination, data=papers[start:end], visual_data=visual_data)


@paper_app.route('/upload_paper', methods=['POST'])
def upload_paper():
    dit = request.form.to_dict()
    print(dit)
    insert_paper(dit)
    return redirect('/papers')


if __name__ == '__main__':
    pass
