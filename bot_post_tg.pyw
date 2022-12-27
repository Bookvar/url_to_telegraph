
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
$ echo "telegraph==2.2.0" >> requirements.txt
$ echo "beautifulsoup4==4.11.1" >> requirements.txt

$ pip install -r requirements.txt
$ deactivate
'''

import time
from datetime import date, timedelta
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
        print(id_article + ' уже был')
    else:
        print(id_article + ' обработка')
        #  обрабатываем найденный пост

        #open tab
        # driver.find_element(By.TAG_NAME,'body').send_keys(Keys.COMMAND + 't')
        # You can use (Keys.CONTROL + 't') on other OSs

        # сохраняем десктриптор текущего окна
        window_before = driver.window_handles[0]
        # Load a page

        # открыть новую вкладку
        driver.execute_script("window.open()")
        # сохраняем десктриптор нового окна
        window_after = driver.window_handles[1]
        # переключаемся на новую вкладку
        driver.switch_to.window(window_after)
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
        # driver.find_element(By.TAG_NAME,'body').send_keys(Keys.COMMAND + 'w')

        #  закрываем вкладку
        driver.close()
        #  переключаемся на старое окно
        driver.switch_to.window(window_before)


        #  постим телеграф в телеграм
        if title !='':    
             
            full_caption = ('<b>'+ title +'</b> \n\n') + ('' if announce_text == '' else (announce_text + '\n\n')) + (article_blocks_all.lstrip('\n'))
            # хвостик к тексту поста с сылкой на телеграф
            tail_caption = '<a href="'+ url_telegraph +'"> ... читать полностью</a>'
            # подрезаем текст исходя из ограничения в 1024 символа для caption
            # минусуя его длину на длину хвостика и сдвигаясь к ближайшему переносу справа 
            # то есть обрезаем строку на 1000 символов минус длина хвоста
            part_caption = full_caption[:full_caption[:800-len(tail_caption)].rfind('\n\n')]
            #  проверяем незакрытые теги для добавления их
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
                    if tag in ('<...>'):
                        escaped_tag = tag.replace('<','&lt')
                        escaped_tag = escaped_tag.replace('>','&gt')
                        part_caption = part_caption.replace(tag, escaped_tag)
                        #  
                        pos = pos - len(tag) # это не тэг - игнорируем 
                        # pass
                    else: 
                        closed_tags += closed_tag
            caption =  part_caption + closed_tags + tail_caption

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
    # options.headless = True
    service = Service(r'C:\bot\statbot\BrowserDrivers\geckodriver.exe')
    driver = Firefox(service=service, options=options)

    ''' 
    # ВАРИАНТ 1 - брать с ленты архива сайта (минус - видим только 20 последних статей)
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
    # ВАРИАНТ 2 - брать с xml ленты архива сайта (распарсим сразу два дня - вчера и сегодня)
    # идём на сайт в ленту архива новостей
    today = date.today()
    yesterday = today - timedelta(days=1)
    today_str = today.strftime('%Y%m%d')
    yesterday_str = yesterday.strftime('%Y%m%d')
    xmls = ['https://ukraina.ru/archive/'+today_str+'/?xml',
            'https://ukraina.ru/archive/'+yesterday_str+'/?xml'
            ]

    xml_archives = []
    for xml in xmls:
        driver.get(xml) 
        time.sleep(1)
        # 
        try:
            pager = driver.find_element(By.CSS_SELECTOR, 'pager[view="pager_no_script"]')
        except  Exception as e:
            # NoSuchElementException
            print(e)
            print("Pager не найден " + time.strftime('%Y-%m-%d %H:%M'))
            print("Берём " + xml)
            xml_archives.append(xml) 
            continue
        else:    
            # pager = driver.find_element(By.CSS_SELECTOR, 'pager[view="pager_no_script"]')
            pages = pager.find_elements(By.CSS_SELECTOR, 'page')
            n=''
            for page in pages:
                url = page.get_attribute('url')
                param = page.get_attribute('param')
                if param is None:
                    xml_archives.append('https://ukraina.ru'+url+'&xml') 
                    n = page.get_attribute('n')
                if param == 'last' and n != page.get_attribute('n'):
                    xml_archives.append('https://ukraina.ru'+url+'&xml') 
    # print('Порядок страниц архива за сегодня и вчера от свежего к старому')
    # for xml_archive in xml_archives:
    #     print(xml_archive) 
    # print('-------------------------------------------------------')
    
    list_articles = []
    for xml_archive in reversed(xml_archives):
        print(xml_archive) 
        driver.get(xml_archive) 
        time.sleep(1)
        try:
            list_archive = driver.find_element(By.CSS_SELECTOR, 'list[sid="archive"]')
            #  проскролим браузер
            # for i in range(0, 3):
            #     html.send_keys(Keys.END)
            #     time.sleep(1)
            
            list_items = list_archive.find_elements(By.TAG_NAME, 'article')
            for list_item in reversed(list_items):
                # print(list_item.get_attribute('id'))
                id_article = list_item.get_attribute('id')
                tag_url = list_item.find_element(By.TAG_NAME, 'url')
                # короткая ссылка на статью
                short_url_article = tag_url.text
                # print(short_url_article)
                
                full_url_article = 'https://ukraina.ru' + short_url_article
                need_to_post = False

                # Проверка на пост по галочке "Экспорт в телеграм"
                send_to_telegram = list_item.find_element(By.TAG_NAME, 'send_to_telegram')
                if send_to_telegram.text == '1':
                    need_to_post = True
                
                # Проверка на пост по белому списку тегов
                # список тегов
                list_tags = list_item.find_elements(By.CSS_SELECTOR, 'list[type="tag"]')
                for list_tag in list_tags:
                    # выделяем текущий тег из списка тегов статьи
                    data_sid = list_tag.get_attribute('sid')
                    # if data_sid =='exclusive' or data_sid == 'interview' or data_sid == 'opinion':
                    #  проверяем на вхождение в белый список тега для экспорта
                    if data_sid in ('exclusive', 'interview','opinion'):
                        need_to_post = True
                        break

                # Тестирую по любым статьям отправлю все 
                # need_to_post = True

                # если статью надо постить
                if need_to_post:
                    # print('Надо постить - добавим в список')
                    list_articles.append(full_url_article) 
        except  Exception as e:
            # NoSuchElementException
            print(e)
            continue
    
    description = ""    
    time.sleep(2)
    for url_article in list_articles:
        post_to_tg(driver, url_article)
    driver.quit()

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    i = 0
    while True:
        print("Шаг "+str(i)+ '. '+ time.strftime('%Y-%m-%d %H:%M'))
        main()  # то запускаем функцию main()
        print("Выдерживаем паузу...")
        time.sleep(300)
        i = i + 1


