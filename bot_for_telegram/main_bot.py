import telebot
import psycopg2
import time as time_main
from psycopg2 import Error
import base64
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ПОЛУЧЕНИЕ ТОКЕНА ИЗ ФАЙЛА С ТОКЕНОМ
try:
    with open('token.txt') as token:
        content = token.read()
except:
    print('Файла с токеном нет в папке!')

bot = telebot.TeleBot(content)

# ОБОЗНАЧЕНИЕ ВСЕХ ТИПОВ СООБЩЕНИЙ ДЛЯ БОТА
CONTENT_TYPES = ["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact",
                 "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
                 "group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                 "migrate_from_chat_id", "pinned_message"]


@bot.message_handler(content_types=CONTENT_TYPES)
def main(message):  
    if message.chat.type == 'group':
        print(message.chat.id)
        print(message.photo)
        # КОНЕКТ К БД
        connection = psycopg2.connect(
            user="postgres",
            password="roma.ru12",
            host="127.0.0.1",
            port="5432",
            database="postgres_db")
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()


        cursor.execute(
            "SELECT CHAT_ID from TELEGRAM_CHATS_ID"
        )

        chats = list(map(lambda chat: chat[0], cursor.fetchall()))

        if message.chat.id in chats:
        # ЛОГИРОВАНИЕ ДЛЯ ГРУППОВОГО ЧАТА
            
                # КОНЕКТ К БД
                connection = psycopg2.connect(
                    user="postgres",
                    password="roma.ru12",
                    host="127.0.0.1",
                    port="5432",
                    database="postgres_db")
                connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                # Курсор для выполнения операций с базой данных
                cursor = connection.cursor()

                # ПРОВЕРКА ТЕКСТОВОЕ ЛИ СООБЩЕНИЕ
                if message.text != None:
                    print('text')
                    # ЕСЛИ СООБЩЕНИЕ ПРОСТОЕ
                    if message.reply_to_message == None:
                        insert_query = \
                            rf" INSERT INTO logging_messages (TELEGRAMUSERID, MESSAGE, MESSAGEID) VALUES ({message.from_user.id}, '{message.text}', {message.message_id})"
                    # ЕСЛИ ОТВЕТ НА СООБЩЕНИЕ
                    else:
                        insert_query = \
                            rf" INSERT INTO logging_messages (TELEGRAMUSERID, MESSAGE, MESSAGEID, RESPONSE_MESSAGE, RESPONSETO) VALUES ({message.from_user.id}, '{message.text}', {message.json['message_id']}, '{message.reply_to_message.json['text']}', '{message.reply_to_message.json['from']['id']}')"
                # ПРОВЕРКА ГОЛОСОВОЕ СООБЩЕНИЕ ИЛИ НЕТ
                elif message.voice != None:
                    print('voice')
                    if message.reply_to_message != None:
                        insert_query = \
                            rf" INSERT INTO logging_messages (TELEGRAMUSERID, VOICE_ID, MESSAGEID, RESPONSETO) VALUES ({message.from_user.id}, '{message.voice.file_id}', {message.json['message_id']}, '{message.reply_to_message.json['from']['id']}')"
                    else:
                        insert_query = \
                            rf" INSERT INTO logging_messages (TELEGRAMUSERID, VOICE_ID, MESSAGEID) VALUES ({message.from_user.id}, '{message.voice.file_id}', {message.json['message_id']})"


                # ПРОВЕРКА ЕСТЬ ЛИ ДОКУМЕНТ В СООБЩЕНИЕ И ПОДПИСЬ К НИМУ
                elif message.document != None:
                    print('Document')
                    file_info = bot.get_file(message.document.file_id)  # НАХОДИМ ID ФАЙЛА
                    download_file = bot.download_file(file_info.file_path)  # СКАЧИВАЕМ ФАЙЛ

                    file_in_base64 = base64.b64encode(download_file).decode()  # КОДИРОВАНИЕ ФАЙЛА В base64

                    # ЗАНЕСЕНИЯ ДАННЫХ В БД В ЗАВИСИМОСТИ БЫЛА ЛИ НАДПИСЬ У ФАЙЛА ИЛИ НЕТ
                    if message.caption != None:
                        insert_query = \
                            rf" INSERT INTO logging_messages (TELEGRAMUSERID, FILE, MESSAGEID, MESSAGE) VALUES ({message.from_user.id}, '{file_in_base64}', {message.json['message_id']}, '{message.caption}')"
                    else:
                        insert_query = \
                            rf" INSERT INTO logging_messages (TELEGRAMUSERID, FILE, MESSAGEID) VALUES ({message.from_user.id}, '{file_in_base64}', {message.json['message_id']})"
                elif message.photo != None:
                    print('Document')
                    file_info = bot.get_file(message.photo[0].file_id)  # НАХОДИМ ID ФАЙЛА
                    download_file = bot.download_file(file_info.file_path)  # СКАЧИВАЕМ ФАЙЛ

                    file_in_base64 = base64.b64encode(download_file).decode()  # КОДИРОВАНИЕ ФАЙЛА В base64

                    # ЗАНЕСЕНИЯ ДАННЫХ В БД В ЗАВИСИМОСТИ БЫЛА ЛИ НАДПИСЬ У ФАЙЛА ИЛИ НЕТ
                    if message.caption != None:
                        insert_query = \
                            rf" INSERT INTO logging_messages (TELEGRAMUSERID, FILE, MESSAGEID, MESSAGE) VALUES ({message.from_user.id}, '{file_in_base64}', {message.json['message_id']}, '{message.caption}')"
                    else:
                        insert_query = \
                            rf" INSERT INTO logging_messages (TELEGRAMUSERID, FILE, MESSAGEID) VALUES ({message.from_user.id}, '{file_in_base64}', {message.json['message_id']})"
                # ДЕЛАЕМ ИЗМЕНЕНИЯ
                print(insert_query)
                cursor.execute(insert_query)
                # ЗАЛИВАЕМ ИХ
                connection.commit()

        if message.chat.type == 'group' and message.text =="/ex":
            print('LOL: ' + str(message.chat.id))

bot.polling(none_stop=True, interval=0)
