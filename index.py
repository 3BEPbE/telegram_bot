import telebot
import pymysql
import json
from pymysql.cursors import DictCursor
from contextlib import closing
import re
from datetime import datetime, timedelta, time

with closing(pymysql.connect(
    host='94.158.54.61',
    user='nick',
    password='R2CLpX@erQJwiPg',
    db='comnet',
    charset='utf8mb4',
    cursorclass=DictCursor
)) as connection:
    with connection.cursor() as cursor:
        query = """
            SELECT title_ru FROM comnet.news; 
        """
        cursor.execute(query)
        for row in cursor:
            print(row)

# connection = pymysql.connect(
#     host='localhost',
#     user='root',
#     password='root',
#     db='comnet',
#     charset='utfmb4',
#     cursorclass=DictCursor
# )

# connection.close()
hello_message_ru = 'Вас приветствует телеграмм бот Comnet. Тут вы можете узнать о последних новостях и акциях, проверить свой лицевой счет, и посмотреть девствующие скидки от партнеров'
hello_message_uz = 'короче на узбеском тугади'
comnet_start = 'Выберите язык'

bot = telebot.TeleBot('1784615137:AAFrypOirDpnweGvvPEXbUQuc0SFScj_yJc')

@bot.message_handler(commands=['start'])
def start_message(message):
    with closing(pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='root',
            db='comnet',
            charset='utf8mb4',
            cursorclass=DictCursor
    )) as connection:
        with connection.cursor() as cursor:
            ban_time = timedelta(minutes=20)
            query = """
                        INSERT INTO telegram_user (chat_id, banned_time) VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE count_time=count_time+1
                    """
            data_employee = (str(message.chat.id), datetime.now())
            cursor.execute(query, data_employee)
            connection.commit()

        with connection.cursor() as cursor:
            query = """
                        SELECT chat_id,count_time,banned_time FROM telegram_user; 
                    """
            cursor.execute(query)
            for row in cursor:
                if row['chat_id'] == str(message.chat.id) and row['count_time'] <= 10:
                    print(row['count_time'])
                elif row['chat_id'] == str(message.chat.id) and row['count_time'] > 10:
                    with connection.cursor() as cursor:
                        query = """
                                    INSERT INTO telegram_user (chat_id, banned_time) VALUES (%s, %s)
                                    ON DUPLICATE KEY UPDATE banned_time=%s
                                """
                        data_employee = (str(message.chat.id), datetime.now(), datetime.now() + ban_time)
                        cursor.execute(query, data_employee)
                        connection.commit()
                        print('каунт больше 10')
                    print('Вы были забанены до ' + str(row['banned_time']))

                # if row['chat_id'] == str(message.chat.id) and row['banned_time'] > datetime.now():
                #     with connection.cursor() as cursor:
                #         query = """
                #                     INSERT INTO telegram_user (chat_id, banned_time) VALUES (%s, %s)
                #                     ON DUPLICATE KEY UPDATE count_time=%s
                #                 """
                #         data_employee = (str(message.chat.id), datetime.now(), 0)
                #         cursor.execute(query, data_employee)
                #         connection.commit()
                #         print('очищен от бана')

        with connection.cursor() as cursor:
            query = """
                SELECT lang, chat_id, selected FROM telegram_lang; 
            """
            cursor.execute(query)
            for row in cursor:
                if row['selected'] == 1:
                    if row['lang'] == 'ru':
                        keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                        keyboard1.row('Тарифы', 'Новости')
                        bot.send_message(message.chat.id, hello_message_ru, reply_markup=keyboard1)
                    elif row['lang'] == 'uz':
                        keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
                        keyboard1.row('Tariffs', 'News')
                        bot.send_message(message.chat.id, hello_message_uz, reply_markup=keyboard1)
                elif row['chat_id'] != message.chat.id or row['selected'] == 0:
                    keyboard1.row('Русский', 'Узбекский')
                    bot.send_message(message.chat.id, comnet_start, reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def set_language(message):
    if message.text.lower() == 'русский':
        with closing(pymysql.connect(
                host='127.0.0.1',
                user='root',
                password='root',
                db='comnet',
                charset='utf8mb4',
                cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = ("INSERT INTO telegram_lang "
                                "(lang, chat_id, selected) "
                                "VALUES (%s, %s, %s)")
                data_employee = ('ru', str(message.chat.id), 1)
                cursor.execute(query, data_employee)
                connection.commit()
    elif message.text.lower() == 'узбекский':
        with closing(pymysql.connect(
                host='127.0.0.1',
                user='root',
                password='root',
                db='comnet',
                charset='utf8mb4',
                cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = ("INSERT INTO telegram_lang "
                         "(lang, chat_id, selected) "
                         "VALUES (%s, %s, %s)")
                data_employee = ('uz', str(message.chat.id), 1)
                cursor.execute(query, data_employee)
                connection.commit()
    elif message.text.lower() == 'тарифы':
        with closing(pymysql.connect(
                host='127.0.0.1',
                user='root',
                password='root',
                db='comnet',
                charset='utf8mb4',
                cursorclass=DictCursor
        )) as connection:
            with connection.cursor() as cursor:
                query = """
                    SELECT chat_id,count_time,banned_time FROM telegram_user; 
                """
                cursor.execute(query)
                for row in cursor:
                    with connection.cursor() as cursor:
                        query = """
                            INSERT INTO telegram_user (chat_id,count_time,banned_time) VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE count_time=count_time+1      
                        """
                        ban_time = timedelta(minutes=30)
                        data_employee = (str(message.chat.id), row['count_time'] + 1, datetime.now() + ban_time)
                        cursor.execute(query, data_employee)
                        connection.commit()

        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/tariffs/LMINI-min.jpg')
        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/tariffs/L+-min.jpg')
        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/tariffs/M+-min.jpg')
        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/tariffs/S+-min.jpg')
        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/tariffs/XL+-min.jpg')

        # with closing(pymysql.connect(
        #         host='94.158.54.61',
        #         user='nick',
        #         password='R2CLpX@erQJwiPg',
        #         db='comnet',
        #         charset='utf8mb4',
        #         cursorclass=DictCursor
        # )) as connection:
        #     with connection.cursor() as cursor:
        #         query = """
        #             SELECT size,price FROM comnet.tariffs ORDER BY created_at DESC;
        #         """
        #         cursor.execute(query)
        #         for row in cursor:
        #             bot.send_message(message.chat.id, 'Название: ' + row['size'] + '  Цена:' + row['price'])
        #             print(row)

    elif message.text.lower() == 'новости':
        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/akci/1.jpeg')
        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/akci/2.jpeg')
        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/akci/3.jpeg')
        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/akci/4.jpeg')
        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/akci/5.jpeg')
        bot.send_photo(message.chat.id, 'https://serv.comnet.uz/telegram/akci/6.jpeg')
        # with closing(pymysql.connect(
        #         host='94.158.54.61',
        #         user='nick',
        #         password='R2CLpX@erQJwiPg',
        #         db='comnet',
        #         charset='utf8mb4',
        #         cursorclass=DictCursor
        # )) as connection:
        #     with connection.cursor() as cursor:
        #         query = """
        #             SELECT title_ru, short_text_ru FROM comnet.news ORDER BY created_at DESC LIMIT 3;
        #         """
        #         cursor.execute(query)
        #         for row in cursor:
        #             bot.send_message(message.chat.id, row['title_ru'] + ':' + row['short_text_ru'])
                    # print(row['short_text_ru'])

# @bot.message_handler(commands=['start'])
# def start_message(message):
#     bot.send_message(message.chat.id, 'Привет из питона')

# @bot.message_handler(commands=['comnet'])
# def start_message(message):
#     bot.send_message(message.chat.id, 'Кирил поверь это тебе не нужно!')
#
# @bot.message_handler(content_types=['text'])
# def send_text(message):
#     if message.text.lower() == 'привет':
#         bot.send_message(message.chat.id, 'Привет, мой создатель')
#     elif message.text.lower() == 'пока':
#         bot.send_message(message.chat.id, 'Прощай, создатель')
#     elif message.text.lower() == 'кирилл':
#         bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAECE7xgVHyzLqUWoDflZouh8Io8y87tpQACBAADqq_VKsetrKoxJwRyHgQ')
#     elif message.text.lower() == 'давид':
#         bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAECE75gVH2vjU7mNeu1xWLXI-88vEdxwAACAgADqq_VKthPqgRyCdtSHgQ')
#     elif message.text.lower() == 'новости':
#         with closing(pymysql.connect(
#                 host='94.158.54.61',
#                 user='nick',
#                 password='R2CLpX@erQJwiPg',
#                 db='comnet',
#                 charset='utf8mb4',
#                 cursorclass=DictCursor
#         )) as connection:
#             with connection.cursor() as cursor:
#                 query = """
#                     SELECT title_ru, short_text_ru FROM comnet.news ORDER BY created_at DESC LIMIT 3;
#                 """
#                 cursor.execute(query)
#                 for row in cursor:
#                     bot.send_message(message.chat.id, row['title_ru'] + ':' + row['short_text_ru'])
#                     print(row['short_text_ru'])
#     elif message.text.lower() == 'тарифы':
#         with closing(pymysql.connect(
#                 host='94.158.54.61',
#                 user='nick',
#                 password='R2CLpX@erQJwiPg',
#                 db='comnet',
#                 charset='utf8mb4',
#                 cursorclass=DictCursor
#         )) as connection:
#             with connection.cursor() as cursor:
#                 query = """
#                     SELECT size,price FROM comnet.tariffs ORDER BY created_at DESC;
#                 """
#                 cursor.execute(query)
#                 for row in cursor:
#                     bot.send_message(message.chat.id, 'Название: ' + row['size'] + '  Цена:' + row['price'])
#                     print(row)


bot.polling()
