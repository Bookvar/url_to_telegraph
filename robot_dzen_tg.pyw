
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

'''        
title = '"Прежде всего здесь становятся бойцами": глава "Ночных волков" Донбасса о жизни на войне. ВИДЕО'
photo = 'https://avatars.dzeninfra.ru/get-zen_doc/4387099/pub_6360e166e4cecd073b5cbda3_6360e166e4cecd073b5cbdf0/smart_crop_516x290'
href = 'https://dzen.ru/a/Y2DhZuTOzQc7XL2j'
text = '"Ночные волки" сейчас, пожалуй, самый известный мотоклуб России.\
    Донбасское отделение байкеров этого клуба принимает участие\
    в боевых действиях с первых дней войны 2014 года.\
    Есть ли какие-то особенности участия мотоциклистов в боевых действиях?\
    Что для них патриотизм? Каким они видят будущее?\
    Об этом и не только мы пообщались с руководителем отделения "Донбасс"\
    мотоклуба "Ночные волки" Виталием Кишкиновым:\
    0:03 - "Ночные волки" на войне;\
    4:16 - Особенности участия мотоциклистов в боевых действиях;...'

caption = '<b>'+ title +'</b>\n\n' + text +'\n\n <a href="'+ href +'">Читать источник</a>'
# <a href="http://www.example.com/">inline URL</a>
# caption = "<b>"+ title +"</b>"+ text +   "<a href=" + href + ">Читать источник</a>"
url = "https://api.telegram.org/bot"
url += token
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
    # return url_tg_post
if r.status_code != 200:
    raise Exception("post_Photo error")
'''

import sqlite3


def id_post_exist(id_dzen_post):
    conn = sqlite3.connect('./data/dzen_urls.db')
    cur = conn.cursor()
    cur.execute("SELECT id_dzen_post FROM urls where id_dzen_post = '"+id_dzen_post+"'")
    rows = cur.fetchall()
    cur.close()
    post_exist = False
    for result in rows:
        # print(result[0])
        post_exist = True
    return post_exist


def main():
    #  Подготавливаем webdriver
    profile_path = r'C:\Users\mitkevich\AppData\Roaming\Mozilla\Firefox\Profiles\7j0x0pgq.default-esr-2'
    options = Options()
    options.set_preference('profile', profile_path)
    options.headless = True
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
    # идём на сайт
    driver.get("https://dzen.ru/ukraina.ru")
    # try:
    html = driver.find_element(By.TAG_NAME,'html')
    #  проскролим браузер
    for i in range(0, 3):
        html.send_keys(Keys.END)
        time.sleep(1)
    
    feed__rows = driver.find_elements(By.CLASS_NAME, 'feed__row')
    for feed__row in reversed(feed__rows):
        print(feed__row.get_attribute('id'))
        feed_item = feed__row.find_element(By.CLASS_NAME, 'feed__item')
        # берём id feed_item 
        id_feed_item = feed_item.get_attribute('id')
        print(id_feed_item)
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



    description = ""    
    time.sleep(5)
    driver.quit()


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    i = 0
    while True:
        print("Бесконечный цикл. Шаг "+str(i))
        main()  # то запускаем функцию main()
        print("Выдерживаем паузу...")
        time.sleep(300)
        i = i + 1


