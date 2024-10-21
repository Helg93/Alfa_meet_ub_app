import telebot
import sqlite3
import random
import time
from telebot import types

# Токен бота
API_TOKEN = '7641721252:AAERTUpL3kSjd3woaEcOVwGAeOnA4GQ_ZwI'

bot = telebot.TeleBot(API_TOKEN)

# Подключение к базе данных SQLite
conn = sqlite3.connect('colleagues.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы users, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER UNIQUE,
        name TEXT,
        department TEXT,
        position TEXT,
        city TEXT,
        username TEXT,
        last_interaction INTEGER DEFAULT 0  -- Время последнего получения контакта в виде UNIX-времени
    )
''')
conn.commit()

user_interactions = {}

# Функция для регистрации пользователя
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """Привет! 👋​
        Я бот CX Team meet up 🤖
        Каждую неделю ты можешь получать один контакт интересного собеседника из школы CX экспертов.

        Даже если встречи случайные, у нас схожие цели, амбиции и интересы.

        CX Team meet up — это возможность:
        ▪️ познакомиться с другими учениками школы
        ▪️ найти полезные контакты
        ▪️ обменяться опытом с коллегами

        Продолжая, ты соглашаешься на обработку персональных данных.
        """)

    bot.send_message(message.chat.id, "Пожалуйста, введите ваше имя и фамилию:")
    bot.register_next_step_handler(message, get_name)

# Получаем имя и фамилию
def get_name(message):
    name = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id, "Укажите вашу дирекцию:")
    bot.register_next_step_handler(message, get_department, name)

# Получаем дирекцию
def get_department(message, name):
    department = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id, "Укажите вашу должность:")
    bot.register_next_step_handler(message, get_position, name, department)

# Получаем должность
def get_position(message, name, department):
    position = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id, "Укажите город, в котором вы работаете:")
    bot.register_next_step_handler(message, get_city, name, department, position)

# Получаем город и сохраняем данные пользователя
def get_city(message, name, department, position):
    city = message.text
    chat_id = message.chat.id
    
    # Получаем username пользователя
    username = message.from_user.username or 'не указан'

    # Сохраняем данные пользователя в базу данных
    cursor.execute('''
        INSERT OR REPLACE INTO users (chat_id, name, department, position, city, username)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (chat_id, name, department, position, city, username))
    conn.commit()

    bot.send_message(chat_id, f"Спасибо, {name}, регистрация завершена!") 
    
    # Добавляем кнопку для получения контакта коллеги
    send_get_colleague_button(chat_id)



# Функция для отправки кнопки "Получить контакт коллеги"
def send_get_colleague_button(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    get_colleague_button = types.KeyboardButton("Получить контакт коллеги")
    markup.add(get_colleague_button)
    bot.send_message(chat_id, "Теперь вы можете получить контакт коллеги, и написать ему:", reply_markup=markup)

# Обработка нажатия кнопки "Получить контакт коллеги"
@bot.message_handler(func=lambda message: message.text == "Получить контакт коллеги")
def handle_get_colleague(message):
    chat_id = message.chat.id
    
    # Проверяем дату последнего взаимодействия
    cursor.execute('SELECT last_interaction FROM users WHERE chat_id = ?', (chat_id,))
    last_interaction = cursor.fetchone()[0]
    current_time = int(time.time())

    # Ограничение в 7 дней (604800 секунд)
    one_week_seconds = 7 * 24 * 60 * 60

    if current_time - last_interaction >= one_week_seconds:
        send_random_colleague(chat_id)
    else:
        # Рассчитываем, сколько времени осталось до следующего запроса
        remaining_time = one_week_seconds - (current_time - last_interaction)
        days_left = remaining_time // (24 * 60 * 60)
        bot.send_message(chat_id, f"Вы уже получили контакт коллеги на этой неделе. Попробуйте снова через {days_left} дн.")

def send_random_colleague(chat_id):
    # Получаем всех пользователей, кроме текущего
    cursor.execute('SELECT * FROM users WHERE chat_id != ?', (chat_id,))
    colleagues = cursor.fetchall()

    # Если пользователя еще нет в словаре взаимодействий, добавляем его
    if chat_id not in user_interactions:
        user_interactions[chat_id] = set()  # Используем множество для хранения уникальных контактов

    # Фильтруем коллег, с которыми пользователь еще не знаком
    unknown_colleagues = [colleague for colleague in colleagues if colleague[1] not in user_interactions[chat_id]]

    if unknown_colleagues:
        # Выбираем случайного коллегу, с которым пользователь еще не знаком
        colleague = random.choice(unknown_colleagues)

        # Добавляем коллегу в список знакомых
        user_interactions[chat_id].add(colleague[1])

        # Обновляем время последнего взаимодействия
        current_time = int(time.time())
        cursor.execute('UPDATE users SET last_interaction = ? WHERE chat_id = ?', (current_time, chat_id))
        conn.commit()

        # Формируем информацию о коллеге
        colleague_info = (
            f"Ваш новый коллега для знакомства:\n"
            f"Имя: {colleague[2]}\n"
            f"Дирекция: {colleague[3]}\n"
            f"Должность: {colleague[4]}\n"
            f"Город: {colleague[5]}\n"
        )
        
        # Добавляем строку с TG, если есть username
        if colleague[6] != 'не указан':
            colleague_info += f"TG: t.me/{colleague[6]}"
        else:
            colleague_info += "TG: не указан"

        bot.send_message(chat_id, colleague_info)
    else:
        # Если пользователь познакомился со всеми
        bot.send_message(chat_id, "Вы уже со всеми познакомились :)")

# Запуск бота
bot.polling(none_stop=True)
