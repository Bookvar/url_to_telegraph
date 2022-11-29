
part_caption = '<b>История с таможней, давление на УПЦ. Итоги 27 ноября на Украине</b>\n\n<b>В Федеральной таможенной службе прояснили ситуацию с грузами двойного назначения для СВО. Служба безопасности Украины продолжает обыски в храмах Украинской православной церкви</b>Вечером 27 ноября бывший народный депутат Украины, спикер парламента Новороссии Олег Царёв рассказал о том, что возникшие на таможне проблемы с грузами двойного назначения, <b>на которые ранее пожаловались волонтёры, решен'
tail_caption ='<a href="https://telegra.ph/Istoriya-s-tamozhnej-davlenie-na-UPC-Itogi-27-noyabrya-na-Ukraine-11-28"> ... читать полностью</a>'
pos = len(part_caption)
closed_tags = ''
while (pos > 0):
    pos_tag_r = part_caption[:pos].rfind('>')
    pos_tag_l = part_caption[:pos_tag_r].rfind('<')
    tag = part_caption[pos_tag_l:pos_tag_r+1]
    pos = pos_tag_l-1
    if tag[1] == '/':
        open_tag = tag.replace('</', '<')
        pos = part_caption[:pos].rfind(open_tag)
    else:
        closed_tag = tag.replace('<', '</')
        closed_tags += closed_tag




'''
import logging
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
    
class message:
    class sender_chat:
        id = 555
        # sender_chat = None
    # sender_chat.id == GROUP_ID
    text = "Привет"

GROUP_ID = 777
# message.sender_chat = None # 777
message.sender_chat.id =  777
content_types="text"

result = (lambda message: message.text != "" and message.sender_chat.id == GROUP_ID and message.chat.type=='supergroup', content_types=="text")

res = False if (message.sender_chat is None) else message.sender_chat.id == GROUP_ID
print(message.sender_chat.id)
print(result)
'''
# import sqlite3
# conn = sqlite3.connect('./data/urls.db')
# cur = conn.cursor()
# cur.execute('CREATE TABLE urls(url_ru_post TEXT, url_en_post TEXT)')

'''
import sqlite3
conn = sqlite3.connect('./data/urls.db')
cur = conn.cursor()
# cur.execute("SELECT url_en_post FROM urls where url_ru_post = 'https://t.me/Kedr_ru/736'")
# cur.execute("SELECT url_en_post FROM urls ")
cur.execute("SELECT * FROM urls ")
# cur.execute("DELETE  FROM  urls ")
# conn.commit()
list_urls = cur.fetchall()
print(list_urls) # or use fetchone()
for url in  list_urls:
    print(url)
'''




'''
def ru_post_exist(url_ru_post):
    cur.execute("SELECT url_en_post FROM urls where url_ru_post = '"+url_ru_post+"'")
    rows = cur.fetchall()
    post_exist = False
    for result in rows:
        # print(result[0])
        post_exist = True
    return post_exist

url_ru_post = 'https://t.me/Kedr_ru/12057'
if ru_post_exist(url_ru_post):
    print('Есть')
else:
    print('Нет')




[('https://t.me/Kedr_ru/693', 'https://t.me/marmit/1281'), ('https://t.me/Kedr_ru/694', 'https://t.me/marmit/1282')]
'''


'''
new_text='<b>🇪🇪Gloomy forecast from Tallinn.\n\n</b>The vice-mayor of the Estonian capital urges to prepare for "draconian prices" for gas.\n\n<i>"People will simply not be able to pay for it. It is possible that gas will stop coming at all,"</i><b></b> he stressed.\n\nHeating with expensive <a href="https://t.me/Kedr_ru/693">firewood</a> is also not an option.\n\n<i>Question — how quickly will Estonia return to the Stone Age thanks to sanctions?\n\n</i>'
new_text='<b>🇪🇪Gloomy for https://t.me/Kedr_ru/693'
index_https = new_text.find("https://t.me/")
index_tag_close = new_text.find('>',index_https)-1

text2 = new_text.replace(new_text[index_https:index_tag_close], "0123456789")
print(text2)
print("Всё")
# new_text = new_text.replace (https://t.me/, new [, count]). 
'''