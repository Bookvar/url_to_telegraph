import asyncio
import datetime
import logging
import requests

# для перевода
import csv
import os
from typing import List

import aiosqlite
import sqlite3
from aiogram import Bot, Dispatcher, types
# from handlers import different_types

# выборка скрытых значений
from data import config
import answer_msgs
#  Инициализируем значения
API_KEY = config.API_KEY
GROUP_ID = config.GROUP_ID
my_channel_id = config.my_channel_id # 369988379 marmit my_channel_id = -1001196628456 # kedr

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# для проверки в кедр отправяю таджикистан
# answer_msg_kedr_ru = answer_msg_Sputnik_Tajikistan
# ---------------
answer_msg = ''
if GROUP_ID == config.id_kedr_ru:
    answer_msg = answer_msgs.answer_msg_kedr_ru
if GROUP_ID == config.id_sputniklive:
    answer_msg = answer_msgs.answer_msg_sputniklive
if GROUP_ID == config.id_Sputnik_Tajikistan:
    answer_msg = answer_msgs.answer_msg_Sputnik_Tajikistan

# ===========================================
#  Код для второго коммента
en_msg=""

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ======================================
# использую только 2 языка.
# Полный список языков можно получить по инструкции https://cloud.yandex.ru/docs/translate/operations/list
class Lang:
    RU = "ru"
    EN = "en"

class Format:
    PLAIN_TEXT = "PLAIN_TEXT"
    HTML = "HTML"

def get_url_en_post(url_ru_post):
    result = url_ru_post
    conn = sqlite3.connect('./data/urls.db')
    cur = conn.cursor()    
    cur.execute("SELECT url_en_post FROM urls where url_ru_post = '"+url_ru_post+"'")
    rows = cur.fetchall()
    for res in rows:
        result = res[0]
    # print(result)    
    return result

import re



def replace_url_tme(texts: List[str]) -> List[str]:
    result=[]
    for text_str in texts:
        urls = re.findall(r'http(?:s)?://\S+', text_str)
        for url_ru_post in urls:
            index_tag_close = url_ru_post.find('">',0)
            if index_tag_close > 0:
                url_ru_post = url_ru_post[0:index_tag_close]
            url_en_post = get_url_en_post(url_ru_post)
            text_str = text_str.replace(url_ru_post, url_en_post)
        result.append(text_str)
    return result
# глоссарий пар перевода 
glossaryPairs = [
    {
        "sourceText": "пасечник",
        "translatedText": "pasechnik"
    },
    {
        "sourceText": "сальдо",
        "translatedText": "saldo"
    }

]                



def translate(texts: List[str], source: str, target: str) -> List[str]:
    # Сформируем заголовок запроса с ключем авторизации
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key {0}".format(API_KEY)
    }

    
    # обрежем идентификатор канала из последней строки текста поста, или заменим его
    
    index_dog = texts[-1].rfind('@')
    if index_dog>-1:
        if texts[-1][index_dog:] == '@SputnikLive</a>' or texts[-1][index_dog:] == '@SputnikLive':
            # 
            # Вариант 2. убрать строчку с подпиской
            index_dog = index_dog - 17
            texts[-1] = texts[-1][:index_dog]
            # 
            # Вариант 1. подмена подписки с оригинала на переводной сайт
            # texts[-1] = texts[-1].replace('"https://t.me/sputniklive"', '"https://t.me/sputnik"')    
            # texts[-1] = texts[-1].replace('@SputnikLive', '@Sputnik')    
        else:
            texts[-1] = texts[-1][:index_dog]
    '''      

    # удаляем последнюю строку с подпиской
    index_dog = texts[-1].rfind('\n\nПодписаться на @')
    # index_dog = texts[-1].rfind('\n\nПодписаться на @')
    texts[-1] = texts[-1][:index_dog]
    # texts[-1] = texts[-1].split('\n\n@')[0] 
    '''
    # Отправим запрос
    response = requests.post(
        "https://translate.api.cloud.yandex.net/translate/v2/translate",
        json={
            "sourceLanguageCode": source,
            "targetLanguageCode": target,
            "format": Format.HTML,
            "texts": texts,
            "glossaryConfig": {
                "glossaryData": {
                    "glossaryPairs": glossaryPairs
                }
            }            
        },
        headers=headers)
    result = [t["text"] for t in response.json()["translations"]]
    # print(result)
    result = replace_url_tme(result)  
    # print(result)
    return result

# Переводить будем с русского на английский
# Задаем соответствующие значения переменным
source = Lang.RU
target = Lang.EN

# ======================================
#  Обработчики сообщений

# dp.include_router(different_types.router)

@dp.message(lambda message: message.text != "" and (False if (message.sender_chat is None) else message.sender_chat.id == GROUP_ID) and message.chat.type=='supergroup', content_types="text")
async def get_message_txt(message: types.Message):
    now = datetime.datetime.now()
    print(now.strftime("%d-%m-%Y %H:%M"))
    print(message.forward_from_message_id)
    # msg_url_ru = 'https://t.me/'+message.forward_from_chat.mention[1:]+'/'+str(message.forward_from_message_id)
    msg_url_ru = 'https://t.me/'+message.forward_from_chat.username+'/'+str(message.forward_from_message_id)
    # Вставка баннера, если не пустой
    if answer_msg != '':
        await message.reply(answer_msg, parse_mode='html', disable_web_page_preview=False)

    # Отправка в другой канал message c английским переводом
    if (my_channel_id != 0):
        msg_ru = message.html_text
        msg_en = translate([msg_ru], source=source, target=target)
        new_text = " ".join(msg_en) 
        msg = await bot.send_message(my_channel_id, new_text,  parse_mode='html', disable_web_page_preview=True, reply_to_message_id = message.forward_from_chat.id)
        # заносим в базу 
        msg_url_en = 'https://t.me/'+msg.chat.username+'/'+str(msg.message_id)
        async with aiosqlite.connect('./data/urls.db') as db:
            sql_str_select = "SELECT url_en_post FROM urls where url_ru_post = '"+msg_url_ru+"'"
            async with db.execute(sql_str_select) as cursor:
                rows = await cursor.fetchall()
                post_exist = False
                for result in rows:
                    post_exist = True
                if not post_exist:
                    insert_str = "INSERT INTO urls VALUES('"+msg_url_ru +"', '"+msg_url_en+"')"
                    await db.execute(insert_str)
                    await db.commit()
        print(msg_url_ru +' -> ' + msg_url_en)

# @dp.edited_message(lambda message: id_sender_chat(message) and message.chat.type=='supergroup', content_types=types.ContentType.TEXT)
@dp.edited_message(lambda message: message.text != "" and (False if (message.sender_chat is None) else message.sender_chat.id == GROUP_ID) and message.chat.type=='supergroup', content_types="text")
async def edit_message_txt(message: types.Message):
    now = datetime.datetime.now()
    print(now.strftime("%d-%m-%Y %H:%M"))
    print(message.forward_from_message_id)
    # генерация полного урла исходного поста
    msg_url_ru = 'https://t.me/'+message.forward_from_chat.username+'/'+str(message.forward_from_message_id)
    if (my_channel_id != 0):
        msg_ru = message.html_text
        msg_en = translate([msg_ru], source=source, target=target)
        new_text = " ".join(msg_en) 
        # узнаем урл английского поста
        async with aiosqlite.connect('./data/urls.db') as db:
            sql_str_select = "SELECT url_en_post FROM urls where url_ru_post = '"+msg_url_ru+"'"
            async with db.execute(sql_str_select) as cursor:
                rows = await cursor.fetchall()
                for result in rows:
                    msg_url_en = result[0]
        # редактирую английское сообщение заменяя исправленнй текст
        index_dog = msg_url_en.rfind('/')+1
        if index_dog>0:
            msg_id = msg_url_en[index_dog:]   
            # dp.edit_message_text aiogram_3?
            # await dp.edit_message_text(chat_id = my_channel_id, message_id=int(msg_id), text = new_text)
            await bot.edit_message_text(chat_id = my_channel_id, message_id=int(msg_id), text = new_text)
        # 
        print(msg_url_ru +' -> ' + msg_url_en)


last_media_group_id = 0
media = [] # types.InputMedia()
msg_media_old=[]

#  Обработка сообщений с видео, фото и т.п
# @dp.message(lambda message: id_sender_chat(message) and message.chat.type=='supergroup', content_types=types.ContentType.ANY)
@dp.message(lambda message: (False if (message.sender_chat is None) else message.sender_chat.id == GROUP_ID) and message.chat.type=='supergroup', content_types=["audio","document","photo","video"])
async def get_message_any(message: types.Message):
    now = datetime.datetime.now()
    print(now.strftime("%d-%m-%Y %H:%M"))
    print(message.forward_from_message_id)
    print(message.media_group_id)
    msg_url_ru = 'https://t.me/'+message.forward_from_chat.username+'/'+str(message.forward_from_message_id)

    global last_media_group_id
    global media
    global msg_media_old

    # Вставка баннера, если не пустой
    if answer_msg != '' and message.caption is not None:
        await message.reply(answer_msg, parse_mode='html', disable_web_page_preview=False)

    # Отправка в другой канал message c английским переводом
    if (my_channel_id != 0):
        if message.media_group_id != last_media_group_id:
            # и очищаем медиагруппу перед новым наполнением
            last_media_group_id = message.media_group_id 
            media = [] # types.InputMedia()
            msg_media_old=[]

        if message.media_group_id is None:
            # и очищаем медиагруппу перед новым наполнением
            last_media_group_id = 0
            media = [] # types.InputMedia()
            msg_media_old=[]

        # Отправка в другой канал message c английским переводом
        # audio
        if message.audio is not None:
            if message.caption is not None:
                msg_en = translate([message.caption], source=source, target=target)
                new_text = " ".join(msg_en) 
            else:
                new_text = ''                 
            media.append(types.InputMediaAudio(media = message.audio.file_id,caption = new_text[:1024] ,parse_mode='html'))
        # документ
        if message.document is not None:
            if message.caption is not None:
                msg_en = translate([message.caption], source=source, target=target)
                new_text = " ".join(msg_en) 
            else:
                new_text = ''                 
            media.append(types.InputMediaDocument(media = message.document.file_id,caption = new_text[:1024] ,parse_mode='html'))
        # фото
        if message.photo is not None and message.photo != []:
            if message.caption is not None:
                msg_en = translate([message.caption], source=source, target=target)
                new_text = " ".join(msg_en) 
            else:
                new_text = ''    
            media.append(types.InputMediaPhoto(media = message.photo[-1].file_id,caption = new_text[:1024] ,parse_mode='html'))
        # видео
        if message.video is not None:
            if message.caption is not None:
                msg_en = translate([message.caption], source=source, target=target)
                new_text = " ".join(msg_en) 
            else:
                new_text = ''                 
            # media.attach_video(types.InputMediaVideo(media = message.video.file_id,caption = new_text ,parse_mode='html'))
            media.append(types.InputMediaVideo(media = message.video.file_id,caption = new_text[:1024] ,parse_mode='html'))

        #  отравляем группу
        await asyncio.sleep(1)
        msg_media = await bot.send_media_group(my_channel_id, media)
        # удаляем предыдущие отправки mediagroup, так как словили новый message из той же медиагруппы
        for msg_old_id in msg_media_old:
            await asyncio.sleep(1)
            # print(' Удаляем -> ' + str(msg_old_id))
            await bot.delete_message(my_channel_id, msg_old_id)
        # запоминаем  id только что отправленных media
        msg_media_old = []
        for msg in msg_media:
            msg_media_old.append(msg.message_id)

        # заносим в базу 
        # msg_url_ru = message.url
        msg_url_en = 'https://t.me/'+msg.chat.username+'/'+str(msg.message_id)
        async with aiosqlite.connect('./data/urls.db') as db:
            async with db.execute("SELECT url_en_post FROM urls where url_ru_post = '"+msg_url_ru+"'") as cursor:
                rows = await  cursor.fetchall()
                post_exist = False
                for result in rows:
                    post_exist = True
                if not post_exist:
                    insert_str = "INSERT INTO urls VALUES('"+msg_url_ru +"', '"+msg_url_en+"')"
                    await db.execute(insert_str)
                    await db.commit()
        print(msg_url_ru +' -> ' + msg_url_en)




@dp.edited_message(lambda message: (False if (message.sender_chat is None) else message.sender_chat.id == GROUP_ID) and message.chat.type=='supergroup', content_types=["audio","document","photo","video"])
async def edit_message_any(message: types.Message):
    now = datetime.datetime.now()
    print(now.strftime("%d-%m-%Y %H:%M"))
    print(message.forward_from_message_id)
    # генерация полного урла исходного поста
    msg_url_ru = 'https://t.me/'+message.forward_from_chat.username+'/'+str(message.forward_from_message_id)
    if (my_channel_id != 0):
        msg_ru = message.html_text
        msg_en = translate([msg_ru], source=source, target=target)
        new_text = " ".join(msg_en) 
        # узнаем урл английского поста
        async with aiosqlite.connect('./data/urls.db') as db:
            sql_str_select = "SELECT url_en_post FROM urls where url_ru_post = '"+msg_url_ru+"'"
            async with db.execute(sql_str_select) as cursor:
                rows = await cursor.fetchall()
                for result in rows:
                    msg_url_en = result[0]
        # редактирую английское сообщение заменяя исправленнй текст
        index_dog = msg_url_en.rfind('/')+1
        if index_dog>0:
            msg_id = msg_url_en[index_dog:]   
            # dp.edit_message_text aiogram_3?
            # await dp.edit_message_text(chat_id = my_channel_id, message_id=int(msg_id), text = new_text)
            await bot.edit_message_caption(chat_id = my_channel_id, message_id=int(msg_id), caption = new_text)
        # 
        print(msg_url_ru +' -> ' + msg_url_en)

# ======================================




# Запуск бота

async def main():

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    # await bot.delete_webhook(drop_pending_updates=True) # если надо очистить очередь
    await dp.start_polling(bot)


if __name__ == "__main__":
    
    asyncio.run(main())

