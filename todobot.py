import json
import requests
import time
import urllib
from dbhelper import DBHelper

db = DBHelper()


TOKEN = "390254848:AAFUl03NVWkYrzlrr-WzwOm7SWG_8YiQF54"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates): # чтобы больше не искал среди старых обновления
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id, reply_markup=None): # объект, включающий клавиатуру
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def handle_updates(updates):
    for update in updates["result"]:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            items = db.get_items(chat)
            # print(items, type(items))
            list_title = [item[0] for item in items]
            # print(list_title, type(list_title))
            if text == "/all":
                # items = db.get_items(chat)
                # print(items, type(items))
                items.sort(key=lambda x:x[1], reverse=True)
                # print(items, type(items))
                message = [item[0] for item in items]
                if message:
                    # print(message, type(message))
                    message = "\n".join(message)
                    send_message(message, chat)
                else:
                    send_message("В списке нет задач. Чтобы создать новую, отправь: Имя задачи <приоритет>", chat)
            elif text == "/help":
                send_message("Добро пожаловать в твой личный To Do list. "
                             "Отправь мне любой текст и я сохраню его как задачу.\n"
                             "\n"
                             "Если ты хочешь выбрать приоритет новой задаче, отправь: "
                             "Имя задачи, а затем  <приоритет> через пробел. "
                             "Вот пример сообщения: Создать задачу <3>\n"
                             "Приоритет - это одно из чисел от 1 до 3."
                             "3 - высокий приоритет, 2 - средний, 1 - низкий.\n"
                             "\n"
                             "Отправь /all, чтобы получить все задачи по приоритету.\n"
                             "Отправь /done, чтобы удалить задачу.\n"
                             "Отправь /help, чтобы посмотреть инструкции."
                             ,
                    chat)
            elif text == "/done":
                keyboard = build_keyboard(list_title)
                # print(items)
                send_message("Выбери задачу, чтобы удалить", chat, keyboard)
            elif text == "/start":
                send_message("Добро пожаловать в твой личный To Do list. "
                             "Отправь мне любой текст и я сохраню его как задачу.\n"
                             "\n"
                             "Если ты хочешь выбрать приоритет новой задаче, отправь: "
                             "Имя задачи, а затем  <приоритет> через пробел. "
                             "Вот пример сообщения:\n"
                             "Создать задачу <3>\n"
                             "Приоритет - это одно из чисел от 1 до 3.\n"
                             "3 - высокий приоритет, 2 - средний, 1 - низкий.\n"
                             "\n"
                             "Отправь /all, чтобы получить все задачи по приоритету.\n"
                             "Отправь /done, чтобы удалить задачу.\n"
                             "Отправь /help, чтобы посмотреть инструкции."
                             ,
                    chat)
            elif text.startswith("/"):
                continue
            elif text in list_title:
                db.delete_item(text, chat)
                items = db.get_items(chat)
                list_title = [item[0] for item in items]
                keyboard = build_keyboard(list_title)
                send_message("Задача удалена", chat, keyboard)
            else:
                print(text, type(text))
                try:
                    text, priority = text.split('<')
                    priority = priority[:-1]
                    print(text, priority)
                    if (priority == '1') or (priority == '2') or (priority == '3'):
                        send_message("Приоритет будет учтён", chat)
                        if text[-1] == ' ':
                            text = text[:-1]
                    else:
                        send_message('Некорректный ввод приоритета. '
                                     'Отправь /help, чтобы получить инструкции', chat)
                        return
                except:
                    priority = '0'
                db.add_item(text, chat, priority)
                send_message("Задача успешно создана!", chat)
                # items = db.get_items(chat)
                # message = "\n".join(items)
                # send_message(message, chat)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def main():
    db.setup()
    last_update_id = None
    while True:
        # print("getting updates")
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)

print(a)
if __name__ == '__main__':
    main()