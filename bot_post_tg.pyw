
'''
firefox.
Драйвер берём https://github.com/mozilla/geckodriver/releases
Последий релиз был 0.29.1
'''

'''
Подготовка виртуального окружения проекта
venv
$ python -m venv venv
$ source venv/scripts/activate
$ echo "requests==2.28.1" > requirements.txt
$ echo "selenium==4.5.0" >> requirements.txt
$ echo "environs==9.5.0" >> requirements.txt
$ echo "validators==0.20.0" >> requirements.txt
$ pip install -r requirements.txt
$ deactivate
'''

import time
import requests
import logging


from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import  Keys
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.proxy import Proxy, ProxyType

import validators
from validators import ValidationFailure
# справочники 
from data import config

import get_url

#  Инициализируем значения
token = config.BOT_TOKEN
# GROUP_ID = config.GROUP_ID
# channel_id = config.my_channel_id # 369988379 marmit my_channel_id = -1001196628456 # kedr
channel_id = config.GROUP_ID

import ctypes  
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)






def is_string_an_url(url_string: str) -> bool:
    result = validators.url(url_string)

    if isinstance(result, ValidationFailure):
        return False

    return result

def send_telegram(caption: str, photo: str):
    url = "https://api.telegram.org/bot"
    url += token
    # method = url + "/sendMessage"
    if photo is None:
        method = url + "/sendMessage"
        r = requests.post(method, data={
            "chat_id": channel_id,
            "text": caption,
            "parse_mode": "HTML"
            })
    else:
        method = url + "/sendPhoto"
        r = requests.post(method, data={
            "chat_id": channel_id,
            "caption": caption,
            "photo": photo,
            "parse_mode": "HTML"
            
            })
        #   .json()
# , parse_mode='HTML'
    if r.status_code == 200:
        pos1 = r.text.find("message_id")
        pos2 = r.text.find(",", pos1)
        pos3 = r.text.find("username")
        pos4 = r.text.find(",", pos3)
        message_id =  r.text[pos1+12:pos2]
        username = r.text[pos3+11:pos4-1]
        url_tg_post = 'https:/t.me/'+username+'/'+message_id
        print(url_tg_post)
        return url_tg_post
    if r.status_code != 200:
        raise Exception("post_Photo error")


import sqlite3

#  проверка, что статью уже постили
def id_post_exist(id_article) -> bool:
    conn = sqlite3.connect('./data/article_urls.db')
    cur = conn.cursor()
    cur.execute("SELECT id_article FROM urls where id_article = '"+id_article+"'")
    rows = cur.fetchall()
    cur.close()
    post_exist = False
    for result in rows:
        # print(result[0])
        post_exist = True
    return post_exist

def get_id_article(url_article):
    id_article = url_article[url_article.rfind('/')+1:-5]
    return id_article

# постим статью 
def post_to_tg(driver, url_article):
    id_article = get_id_article(url_article)  
    if id_post_exist(id_article): # если уже есть в базе
        print('уже был')
    else:
        print('обработка')
        #  обрабатываем найденный пост

        #open tab
        driver.find_element(By.TAG_NAME,'body').send_keys(Keys.COMMAND + 't')
        # You can use (Keys.CONTROL + 't') on other OSs
        # Load a page
        # открываем статью в новой вкладке
        driver.get(url_article)
        time.sleep(1)

        # постим статью в телеграф
        page_telegraph = get_url.create_page_telegraph(url_article)
        # return [url_telegraph, src_img, title, announce_text, article_blocks_all]
        url_telegraph = page_telegraph[0]
        href_image = page_telegraph[1]
        title = page_telegraph[2]
        announce_text = page_telegraph[3]
        article_blocks_all = page_telegraph[4]
        print(url_article + ' -> ' + url_telegraph) # распечатываем адрес страницы

        # закрываем вкладку
        # (Keys.CONTROL + 'w') on other OSs.
        driver.find_element(By.TAG_NAME,'body').send_keys(Keys.COMMAND + 'w')

        #  постим телеграф в телеграм
        if title !='':    
            # caption = '<b>'+ title +'</b>\n\n' + announce_text
            # article_blocks_all = '<div>Американское издание The Wall Street Journal опубликовало сообщение о том, что Саудовская Аравия и другие участники картеля ОПЕК+ обсуждают вопрос об увеличении добычи нефти на 500 тысяч баррелей в сутки. Сейчас объем составляет около 29,7 миллионов баррелей.</div>'
            caption = '<b>'+ title +'</b>' + announce_text + article_blocks_all
            caption = caption[:caption[:1000].rfind('\n\n')-2] +'<a href="'+ url_telegraph +'"> ... читать полностью</a>'
            # caption = caption +'\n\n <a href="'+ url_telegraph +'">Читать полностью</a>'
            url_tg_post = send_telegram(caption, href_image)
            conn = sqlite3.connect('./data/article_urls.db')
            cur = conn.cursor()
            # id_article TEXT, url_article TEXT, url_telegraph TEXT, url_tg_post TEXT 
            insert_str = "INSERT INTO urls VALUES('"+id_article +"', '"+url_article+"', '"+url_telegraph+"', '"+url_tg_post+"')"
            cur.execute(insert_str)
            conn.commit()
            cur.close()
            # пауза, чтобы не было ошибки HTTP 429 too many requests
            time.sleep(10)




def main():

    #  Подготавливаем webdriver
    profile_path = r'C:\Users\mitkevich\AppData\Roaming\Mozilla\Firefox\Profiles\7j0x0pgq.default-esr-2'
    options = Options()
    options.set_preference('profile', profile_path)
    # options.headless = True
    service = Service(r'C:\bot\statbot\BrowserDrivers\geckodriver.exe')
    driver = Firefox(service=service, options=options)
    '''

    binary = FirefoxBinary("C:\\Program Files\\Mozilla Firefox\\firefox.exe")
    profile = FirefoxProfile(
        "C:\\Users\\mitkevich\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\7j0x0pgq.default-esr-2"
    )
    # добвака сокрытия окна браузера (делаем его невидимым) требует добавку в webdriver = webdriver.Firefox(options=opts)
    opts = webdriver.FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(firefox_profile=profile, firefox_binary=binary, options = opts,
                                executable_path="C:\\bot\\statbot\\BrowserDrivers\\geckodriver.exe")
    #  браузер невидим, максимайзить не надо
    # driver.maximize_window()    
    '''  



    # идём на сайт в ленту архива новостей
    driver.get("https://ukraina.ru/archive/")
    # try:
    html = driver.find_element(By.TAG_NAME,'html')
    #  проскролим браузер
    for i in range(0, 3):
        html.send_keys(Keys.END)
        time.sleep(1)
    
    list_items = driver.find_elements(By.CLASS_NAME, 'list-item')
    list_articles = []
    for list_item in reversed(list_items):
        # print(list_item.get_attribute('id'))
        tag_a = list_item.find_element(By.TAG_NAME, 'a')
        # короткая ссылка на статью
        href_item = tag_a.get_attribute('href')
        print(href_item)
        # список тегов
        list_item_tags = list_item.find_element(By.CLASS_NAME, 'list-item__tags')
        list_tags = list_item_tags.find_elements(By.CLASS_NAME, 'list-tag')
        need_to_post = False
        for list_tag in list_tags:
            data_sid = list_tag.get_attribute('data-sid')
            if data_sid == 'exclusive':
                need_to_post = True
                break
        # если статью надо постить
        if need_to_post:
            print('постим')
            list_articles.append(href_item) 


        '''
        #  поиск подходящего класса 
        card_image = feed_item.find_elements(By.CLASS_NAME,"card-image-compact-view")
        if id_post_exist(id_feed_item):  # если уже есть в базе
            print('уже был')
            continue  #  то переходим на следующий пост в дзене
        elif len(card_image)==0:
            print('не подходит по классу')
            continue  #  то переходим на следующий пост в дзене
        else:
            print('обработка')
            #  обрабатываем найденный пост
            # первый искать нельзя, есть посты без картинки
            tags_a = feed_item.find_elements(By.TAG_NAME,"a")
            a_class = ''
            title=''
            href=''
            for tag_a in tags_a:
                if tag_a.get_attribute("aria-label") is None:
                    pass
                else:
                    a_class = tag_a.get_attribute("class")
                    title = tag_a.get_attribute("aria-label")
                    href = tag_a.get_attribute("href")
                    znak = href.find("?")
                    href = href[:znak]
                    break

            print("id: " + id_feed_item)
            print("title: " + title)
            print("href: " + href)
            # if a_class == 'card-video-2-view__clickable':
            #     continue
            # if a_class == 'card-image-compact-view__clickable':    
            #  добавим проверку что пост на просто текстовый
            elem_card_image = feed_item.find_element(By.CLASS_NAME, 'card-image-compact-view' )
            #  если содержит класс _text_only то div с картинкой искать нельзя
            elem_class = elem_card_image.get_attribute("class")
            if  '_text-only' in elem_class.split(" "):
                href_image = None
            else:
                div_image = feed_item.find_element(By.CLASS_NAME, 'card-layer-image-view__image')
                style = div_image.get_property("style")
                href_image = style['backgroundImage'][5:-2]
                print("href image: " + href_image)

            text = ""
            #  если простой пост, а не видео, то там должна быть часть текста статьи
            # if a_class == 'card-image-compact-view__clickable':    
            card_layer = feed_item.find_element(By.CLASS_NAME, 'card-layer-snippet-view')
            text = card_layer.find_element(By.CLASS_NAME, 'zen-ui-line-clamp').text
                # print(text)
            if title !='':    
                caption = '<b>'+ title +'</b>\n\n' + text +'\n\n <a href="'+ href +'">Читать источник</a>'
                
                url_tg_post = send_telegram(caption, href_image)
                conn = sqlite3.connect('./data/dzen_urls.db')
                cur = conn.cursor()
                if (href_image is None):
                    insert_str = "INSERT INTO urls VALUES('"+id_feed_item +"', '"+href+"', '', '"+url_tg_post+"')"
                else:
                    insert_str = "INSERT INTO urls VALUES('"+id_feed_item +"', '"+href+"', '"+href_image+"', '"+url_tg_post+"')"
                cur.execute(insert_str)
                conn.commit()
                cur.close()
                # пауза, чтобы не было ошибки HTTP 429 too many requests
                time.sleep(10)

        '''

    description = ""    
    time.sleep(2)
    print(list_articles)
    # 
    for url_article in list_articles:
        post_to_tg(driver, url_article)






    driver.quit()


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    i = 0
    while True:
        print("Бесконечный цикл. Шаг "+str(i))
        main()  # то запускаем функцию main()
        print("Выдерживаем паузу...")
        time.sleep(300)
        i = i + 1


