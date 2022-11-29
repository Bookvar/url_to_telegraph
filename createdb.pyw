import sqlite3
conn = sqlite3.connect('./data/article_urls.db')
cur = conn.cursor()



# создать базу
# cur.execute('CREATE TABLE urls(id_article TEXT, url_article TEXT, url_telegraph TEXT, url_tg_post TEXT  )')
cur.execute("SELECT id_article FROM urls ")
rows = cur.fetchall()
for row in rows:
    print(row[0])

# почистить базу 
cur.execute("DELETE  FROM  urls ")
conn.commit()


# cur.execute("SELECT id_article FROM urls where id_article = '"+id_article+"'")
cur.execute("SELECT id_article FROM urls ")
rows = cur.fetchall()
for row in rows:
    print(row[0])
conn.close()