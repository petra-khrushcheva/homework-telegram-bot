import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv
from http import HTTPStatus
from exceptions import NoServerResponseError

load_dotenv()

logging.basicConfig(
    format='%(asctime)s, %(levelname)s, %(message)s',
    filemode='a',
    filename='main.log',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info('Отправлено сообщение в чат')
    except telegram.error.TelegramError as error:
        logging.error(f'Не удалось отправить сообщение. {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к эндпойнту Практикума."""
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.RequestException('Неуспешный запрос к серверу') as error:
        logging.error({error})
    if response.status_code != HTTPStatus.OK:
        raise NoServerResponseError(
            'Ответ сервера не является успешным:'
            f' request params = {params};'
            f' http_code = {response.status_code};'
            f' reason = {response.reason}; content = {response.text}'
        )
    return response.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        raise TypeError(
            f'Тип данных ответа API - {type(response)}, ожидаемый - dict'
        )
    if not isinstance(response.get('homeworks'), list):
        hw_list = response.get('homeworks')
        raise TypeError(
            f'Тип данных списка домашних работ - {type(hw_list)},'
            'ожидаемый - list'
        )
    return response.get('homeworks')


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе ее статус."""
    if 'status' not in homework or 'homework_name' not in homework:
        raise KeyError(
            'Информация о домашней работе не содержит ожидаемых данных')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        raise KeyError('Неиспользованный ранее статус домашней работы')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        logging.critical(
            'Отсутствует переменная окружения. Программа остановлена.'
        )
        sys.exit()

    last_error_message = ''

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date', current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                hw_message = parse_status(homeworks[0])
                send_message(bot, hw_message)
            else:
                logging.debug('Статус домашней работы не изменился')
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}', exc_info=True)
            message = f'Сбой в работе программы: {error}'
            if message != last_error_message:
                send_message(bot, message)
                last_error_message = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
