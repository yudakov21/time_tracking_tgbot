import datetime
import json
import telebot
from telebot import types


data_file = 'time_tracking_data.json'
file = open('./mytocken.txt')
mytocken = file.read()
bot = telebot.TeleBot(mytocken)


def load_data():
    try: 
        with open(data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def save_data(data):
    with open(data_file, 'w') as file:
        return json.dump(data, file, indent=4)


def add_activities(activity, start_time, end_time):
    data = load_data()
    data.append({
        'activity': activity,
        'start_time': start_time.strftime('%Y-%m-%d %H:%M'),
        'end_time': end_time.strftime('%Y-%m-%d %H:%M'),
        'date': start_time.strftime('%Y-%m-%d'),
        'duration': str(end_time - start_time)
    }) 
    save_data(data)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Добавить')
    button2 = types.KeyboardButton('Сохраненка')
    button3 = types.KeyboardButton('Выход')
    markup.row(button1,button2)
    markup.row(button3)

    if message.text == '/start':
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!👋\nЯ твой трекер времени. Используй команды и кнопки для управления мной.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Вернул тебя обратно", reply_markup=markup)
        bot.send_message(message.chat.id, "👋", reply_markup=markup)

@bot.message_handler(commands=['add_activity'])
def request_activity_data(message):
    msg = bot.send_message(message.chat.id, "Введите активность, время начала и время окончания в формате:\n 📅 Активность, YYYY-MM-DD HH:MM, YYYY-MM-DD HH:MM")
    bot.register_next_step_handler(msg, process_activity_input)


def process_activity_input(message):
    try:
        # Разбиваем входное сообщение на части с учетом максимального количества разделителей
        parts = [part.strip() for part in message.text.split(',', maxsplit=2)]
        
        # Проверяем, что у нас есть три части: активность, время начала, время окончания
        if len(parts) == 3:
            activity = parts[0]
            start_time = datetime.datetime.strptime(parts[1], '%Y-%m-%d %H:%M')
            end_time = datetime.datetime.strptime(parts[2], '%Y-%m-%d %H:%M')

            # Проверяем, что время начала раньше времени окончания
            if start_time >= end_time:
                bot.send_message(message.chat.id, 'Ошибка: время начала должно быть раньше времени окончания.')
                return
            
            # Добавляем активность
            add_activities(activity, start_time, end_time)
            bot.send_message(message.chat.id, 'Активность добавлена!')
        else:
            bot.send_message(message.chat.id, 'Неверный формат ввода. Попробуйте снова.')
    except Exception:
        bot.reply_to(message, 'Ошибка')


def request_date(message):
    msg = bot.send_message(message.chat.id, "Введите дату в формате YYYY-MM-DD, чтобы узнать активности за этот день 📅")
    bot.register_next_step_handler(msg, show_activities)

def show_activities(message):
    date_requested = message.text.strip()
    data = load_data()
    act_for_day = [activity for activity in data if 'date' in activity and activity['date'] == date_requested]

    if not act_for_day:
        bot.send_message(message.chat.id, 'Нет активностей за этот день((')
        return
    
    response = f'📅 Активности за этот день {date_requested}:\n'
    for i, activity in enumerate(act_for_day, 1):
        response += f"{i}. {activity['activity']} von {activity['start_time']} bis {activity['end_time']}\n"
    bot.send_message(message.chat.id, response)


@bot.message_handler()
def tracker(message):
    if message.text == 'Добавить':
        request_activity_data(message)
    elif message.text == 'Сохраненка':
        request_date(message)
    elif message.text == 'Выход':
        start(message)
    else:
        bot.send_message(message.chat.id, 'Повтори запрос')


bot.polling(none_stop=True)
