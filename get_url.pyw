
'''
firefox.
Драйвер берём https://github.com/mozilla/geckodriver/releases
Последий релиз был 0.29.1
'''

'''

python3 -m pip install telegraph
with asyncio support
python3 -m pip install 'telegraph[aio]'

pip install beautifulsoup4

Подготовка виртуального окружения проекта
venv
$ python -m venv venv
$ source venv/scripts/activate
$ echo "requests==2.28.1" > requirements.txt
$ echo "telegraph==2.2.0" >> requirements.txt
    
$ echo "beautifulsoup4==4.11.1" >> requirements.txt
          
# $ echo "selenium==4.5.0" >> requirements.txt
# $ echo "environs==9.5.0" >> requirements.txt
# $ echo "validators==0.20.0" >> requirements.txt
$ pip install -r requirements.txt
$ deactivate
'''

'''
import requests
#создаем параметры для создания профиля
data={
    'short_name':'', # ОБЯЗАТЕЛЬНЫЙ ПАРАМЕТР, имя учетной записи, помогает пользователям с несколькими учетными записями запомнить, какая сейчас используются. Отображается пользователю над кнопкой «Изменить / Опубликовать» на Telegra.ph, другие пользователи не видят это имя.
    'author_name':'', # Не обязательно. Указывает автора в заголовке странцы
    'author_url':'' # Не обязательно. Ссылка открывается, когда пользователи нажимают на имя автора под заголовком. Это может быть любая ссылка, не обязательно на профиль или канал Telegram.
}
#отправляем запрос ответ понадобится, запишем в переменную:
result=requests.get("https://api.telegra.ph/createAccount?", params=data)
'''

# from telegraph import Telegraph

# telegraph = Telegraph()
# telegraph.create_account(short_name='1337')

# response = telegraph.create_page(
#     'Hey',
#     html_content='<p>Hello, world!</p>'
# )
# print(response['url'])


import time
import requests
from telegraph import Telegraph
import json
import logging
import urllib3

from bs4 import SoupStrainer, BeautifulSoup

# создадим аккаунт
# result=telegraph.create_account(short_name='marmit')
# В ответ приходит json с токеном и прочим. 
# Токен надо сохранять, я сохраню полученные данные 
# в файл graph_bot.json
# with open('graph_bot.json', 'w', encoding='utf-8') as f:
#     json.dump(graph_bot, f, ensure_ascii=False, indent=4) # сохраняю в файл graph_bot

def create_page_telegraph(url_article):
    http = urllib3.PoolManager()
    # url = 'https://ukraina.ru/20221118/1040954553.html' # с автором без анонса
    url =  url_article #'https://ukraina.ru/20221118/1040956068.html' # без автора с анонсом

    page = http.request('GET', url)
    print(page.status)
    soup = BeautifulSoup(page.data, 'html.parser')

    # Заголовок
    article_title = soup.find(class_='article__title') # тут есть заголовок h1
    title = article_title.text

    # Заходное медиа
    article_announce = soup.find(class_='article__announce') # тут есть картинка
    article_announce_media = article_announce.find('img')
    src_img = article_announce_media.attrs.get('src')
    alt_img = article_announce_media.attrs.get('alt')
    article_announce_media.attrs = {'src':src_img, 'alt':alt_img}
    copyright_img = article_announce.find(class_='media__copyright-item')
    if copyright_img is not None:
        if copyright_img.name == 'div':
            copyright_img.name = 'figcaption'
        copyright_img.attr={}

    announce_media = '<figure>' + str(article_announce_media) + str(copyright_img)+'</figure>'
    # копирайт медиа

    article_author = soup.find(class_='article__author')
    author_name = ''
    if article_author is not None:
        article_author_name = article_author.find(class_='article__author-name')
        author_name = '' if article_author_name is None else article_author_name.text 

    # url автора пока не доразбирал, так как урлы ведут на украина ру, нет смысла
    # article_author_links = article_author.find(class_='article__author-links')
    # if article_author_name is None:
    #     author_url = 'https://xn--h1ajim.xn--p1ai/index.php/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0'
    # else:
    #     author_url = article_author_links.next

    article_announce_text = soup.find(class_='article__announce-text')
    # пусто, если нет анонса
    announce_text = '' if article_announce_text is None else '<b>' + article_announce_text.text + '</b>\n' 
    # class_id = SoupStrainer(attrs={'class': 'article__block', 'data-type':'text'})

    # ВАРИАНТ article__block
    # в этом варианте не получается убрать корневой блок article__block и поднять выше его дочерний article__text
    # а вложенный <p><p>XXX</p></p> не прокатывает
    #  выбираем все блоки статьи
    class_id = SoupStrainer(attrs={'class': 'article__block'})
    article__blocks = BeautifulSoup(page.data, "html.parser", parse_only=class_id)
    
    #  для телеграфа меняем запрещенные теги  и убираем аттрибуты
    #  для телеграмма собираем блок абзацев
    tg_article_blocks_all = ''
    for article__block in article__blocks:
        data_type = article__block.attrs.get('data-type')
        if article__block.name == 'div':
            article__block.name = 'p'
        if  data_type == 'text':
            for div in article__block.contents:
                if div.name == 'div':
                    div.name = 'p'
                div.attrs={}
        else:
            article__block.contents=[]
        # стираем аттрибуты
        article__block.attrs={}
        if article__block.text != '':
            tg_article_blocks_all = tg_article_blocks_all + article__block.getText() + '\n\n'
    
    # удаляем пустые абзацы для телеграф 
    len_ab = len(article__blocks.contents)
    for indx in range(len_ab-1,-1,-1):
        if article__blocks.contents[indx].text=='':
            article__blocks.contents.pop(indx)
    article_blocks_all = article__blocks.prettify()

    telegraph = Telegraph()
    html_content= announce_media + announce_text + article_blocks_all
    access_token = "942ddb15907ba63df3cd71dc8255e5afc7f364213ee732df08ef543fd0a1"
    telegraph = Telegraph(access_token) # передаём токен доступ к страницам аккаунта
    response = telegraph.create_page(
        title = title, # заголовок страницы
        author_name = author_name,
        # author_url = author_url,
        html_content = html_content # ставим параметр html_content, добавляем текст страницы
    )

    url_telegraph = 'https://telegra.ph/{}'.format(response['path'])

    # print(url_telegraph) # распечатываем адрес страницы

    # количество страниц 
    # data={
    #     'access_token': access_token,
    #     'fields':'["short_name","page_count"]'    
    # }
    # account_info=requests.get("https://api.telegra.ph/getAccountInfo?", params=data)
    # print(account_info.json())

    return [url_telegraph, src_img, title, announce_text, tg_article_blocks_all]

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    url_article = 'https://ukraina.ru/20221125/1041214798.html'
    # url_article = 'https://ukraina.ru/20221118/1040956068.html'
    page_telegraph = create_page_telegraph(url_article)
    url_page_telegraph = page_telegraph[0]
    print(url_page_telegraph)
