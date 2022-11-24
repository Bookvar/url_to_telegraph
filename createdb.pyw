import sqlite3
conn = sqlite3.connect('./data/article_urls.db')
cur = conn.cursor()

# создать базу
# cur.execute('CREATE TABLE urls(id_article TEXT, url_article TEXT, url_telegraph TEXT, url_tg_post TEXT  )')

# почистить базу 
cur.execute("DELETE  FROM  urls ")
conn.commit()

conn.close()