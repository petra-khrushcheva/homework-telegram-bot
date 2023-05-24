# Homework telegram bot

### Описание
Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.
***
### Технологии
Python 3.7  
python-telegram-bot
***

### Как запустить проект:

Создайте бота в Telegram через BotFather и получите его токен.

Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone git@github.com:petra-khrushcheva/homework-telegram-bot.git
```

```
cd homework-telegram-bot
```

Cоздайте и активируйте виртуальное окружение.
Cоздайте .env-файл и укажите в нем по образцу PRACTICUM_TOKEN (получить токен можно по адресу: https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a), TELEGRAM_TOKEN (токен созданного вами бота), TELEGRAM_CHAT_ID (ваш chat id).

Установите зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```
Запустите проект:

```
python3 main.py
```
Добавьте бота в Telegram и отправьте ему сообщение "/start".