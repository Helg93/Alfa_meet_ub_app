# Telegram Бот для Знакомств среди Коллег

Этот бот помогает сотрудникам банка знакомиться друг с другом. Каждую неделю бот будет предлагать нового коллегу для знакомства. Регистрация проходит через интерфейс бота, а общение через Telegram.

## Основные функции

1. **Регистрация пользователей** — бот собирает данные о сотрудниках (имя, дирекция, должность, город).
2. **Получение контакта коллеги** — раз в неделю бот предоставляет контакт нового коллеги.
3. **Контакты через Telegram** — бот отправляет информацию о коллегах, включая имя, дирекцию, должность, город и, если указано, ссылку на Telegram-аккаунт.

Использование
Регистрация пользователя
Пользователь должен ввести команду /start, чтобы начать процесс регистрации. Бот последовательно соберет следующие данные:

Имя и фамилия
Дирекция
Должность
Город
Получение контакта коллеги
После регистрации пользователь может нажать на кнопку "Получить контакт коллеги", и бот предоставит контакт нового коллеги. Пользователь может получать только одного нового коллегу раз в неделю.

Примечания
Если у пользователя уже есть информация обо всех коллегах, бот уведомит его об этом.
Информация о пользователях хранится локально в базе данных SQLite (colleagues.db).
Требования
Python 3.7+
Библиотеки: pyTelegramBotAPI, sqlite3
