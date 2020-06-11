import pymysql

from elasticsearch import Elasticsearch

db = pymysql.connect(host='127.0.0.1', user='zzn', password='123456',
                     db='uav_ecosystem', cursorclass=pymysql.cursors.DictCursor)

def get_cursor():
    db.ping(reconnect=True)
    cursor = db.cursor()
    return cursor


if __name__ =='__main__':
    cursor = get_cursor()
    sql = 'SELECT postId,title,content FROM post'
    cursor.execute(sql)
    posts = cursor.fetchall()
    cursor.close()
    print(posts[:2])
    es_client = Elasticsearch(hosts=[{"host": "localhost", "port": "9200"}])
    for post in posts:
        es_client.index(index='posts',doc_type='test',body=post)
    
    cursor = get_cursor()
    sql = 'SELECT * FROM uavpapers'
    cursor.execute(sql)
    papers = cursor.fetchall()
    cursor.close()
    print(papers[:2])
    for paper in posts:
        es_client.index(index='papers',doc_type='test',body=paper)
        