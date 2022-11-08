import sqlite3
conn = sqlite3.connect('./data/dzen_urls.db')
cur = conn.cursor()

# создать базу
# cur.execute('CREATE TABLE urls(id_dzen_post TEXT, url_dzen_post TEXT, url_image TEXT, url_tg_post TEXT  )')

# почистить базу 
# cur.execute("DELETE  FROM  urls ")
# conn.commit()

conn.close()