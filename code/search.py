    
from elasticsearch import Elasticsearch
from flask import Blueprint, render_template, request, session, jsonify
from mysql import query_all_papers
from collections import Counter
search_app = Blueprint('search_app', __name__)

@search_app.route('/search',methods=['GET'])
def search():
    keyword = request.args.get('key_word')
    print(keyword)
    es_client = Elasticsearch(hosts=[{"host": "localhost", "port": "9200"}])

    doc = {
        "query":{
            "match":{
                "content":keyword
            }
        }
    }
    searched = es_client.search(index='posts',doc_type='test',body=doc)

    size = searched['hits']['total']['value']
    doc['size'] = size
    searched = es_client.search(index='posts',doc_type='test',body=doc)
    posts = []
    for item in searched['hits']['hits']:
        posts.append(item['_source'])

    all_papers = query_all_papers()
    papers = []
    for paper in all_papers:
        if paper['title'].find(keyword)==-1:
            continue
        else:
            papers.append(paper)
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
    return render_template('search.html',posts=posts,papers=papers,visual_data=visual_data)

if __name__ =='__main__':
    pass