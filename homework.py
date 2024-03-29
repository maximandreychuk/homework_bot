import http
import logging
import os
import requests
import sys
import telegram
import time

from dotenv import load_dotenv
from exceptions import (
    NoSendMessageEx,
    InvalidHttpCodeEx,
    InvalidRequestEx,
    UnknownStatusEx
)

load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filename='logging_for_homework.log',
    format='%(asctime)s -%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_tokens():
    """Проверка токенов. Если их нет - программа останавливается."""
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logger.critical('Где токены?')
        sys.exit()


def send_message(bot, message):
    """С помощью этой функции отправляем сообщение в чат."""
    try:
        logger.debug('Отправка сообщения..')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Успешная отправка сообщения!')
    except Exception:
        logger.error('Не получается отправить сообщение')
        raise NoSendMessageEx('Не получается отправить сообщение')


def get_api_answer(timestamp):
    """Получаем результат запроса к API."""
    try:
        PAYLOAD = {'from_date': timestamp}
        logger.debug('Отправка запроса к API с '
                     f'headers = {HEADERS} и params = {PAYLOAD}')
        response = requests.get(ENDPOINT, headers=HEADERS, params=PAYLOAD)
        if response.status_code != http.HTTPStatus.OK:
            logger.error(f'Ошибка. Код запроса = {response.status_code}')
            raise InvalidHttpCodeEx('Ошибка. Код запроса'
                                    f' = {response.status_code}')
        return response.json()
    except Exception as error:
        logger.error(f'Ошибка получения request: {error}')
        raise InvalidRequestEx(f'Ошибка получения request: {error}')


def parse_status(homework):
    """Получаем статус последней домашней работы(если она есть)."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if homework_name is not None and status is not None:
        if status in HOMEWORK_VERDICTS:
            verdict = HOMEWORK_VERDICTS.get(status)
            return ('Изменился статус проверки работы'
                    f' "{homework_name}". {verdict}')
        logger.error('Неожиданный статус домашней работы:'
                     f' {verdict}, обнаруженный в ответе API')
        raise UnknownStatusEx('Hеизвестный статус')
    logger.error('Нет ключей')
    raise KeyError('Нет ключей')


def check_response(response):
    """Проверяем наш запрос на предмет различных ошибок."""
    try:
        if not isinstance(response, dict):
            logger.error('Запрос к API вернул не словарь')
            raise TypeError('Запрос к API вернул не словарь')
        if 'homeworks' not in response:
            logger.error('Нет ключа homeworks')
            raise KeyError('Нет ключа homeworks')
        if not isinstance(response['homeworks'], list):
            logger.error('Значение ключа homeworks не list')
            raise TypeError('Значение ключа homeworks не list')
        if not response['homeworks']:
            logger.error('Список пуст')
            raise TypeError('Список пуст')
        return response['homeworks']
    except Exception as error:
        logger.error(error)
        raise TypeError(error)


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            bot.send_message(TELEGRAM_CHAT_ID, message)

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
