import requests
import telegram
import os
import logging
import requests

from dotenv import load_dotenv
from exceptions import MyException

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='logging_for_homework.log', 
    format='%(asctime)s -%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
CHAT_ID=549065222


def check_tokens():
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN is None:
        logger.critical('Где токены?')
        raise MyException('Где токены?')


def get_api_answer(timestamp):
    try:
        PAYLOAD = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=PAYLOAD)
        if response.status_code != 200:
            logger.error(f'Ошибка. Код запроса = {response.status_code}')
            return print(response.json())
        return print(response.json())
    except Exception:
        logger.error('Возможно, проблема с ENDPOINT')



def send_message(bot, message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
        logger.debug('Успешная отправка сообщения!')
    except Exception:
        logger.error('Не получается отправить сообщение')



def parse_status(homework):
    homework_name=homework[0].get("homework_name")
    verdict=homework[0].get("status")
    if verdict in HOMEWORK_VERDICTS:
        return print(f'Изменился статус проверки работы "{homework_name}". {HOMEWORK_VERDICTS[verdict]}')
    else:
        logger.error(f"Неожиданный статус домашней работы: {verdict}, обнаруженный в ответе API")




def check_response(response):
    try: 
        if not isinstance(response, dict):
            logger.error('API вернул не словарь!')
            raise TypeError('API вернул не словарь!')
        if "homeworks" not in response.keys():
            logger.error('Не существующий ключ!')
            raise KeyError('Не существующий ключ!')
        if not isinstance(response["homeworks"], list):
            logger.error("Значение ключа [homeworks] не список!")
            raise TypeError("Значение ключа [homeworks] не список!")
        if not isinstance(response["homeworks"][0], dict):
            logger.info('На заданную дату нет работ')
    except IndexError:
        logger.info('На заданную дату нет работ')

    try:
        if type(response) == dict:
            homeworks = response['homeworks']
            if type(homeworks) == list:
                if "homeworks" in response.keys():
                    return homeworks
                logger.error('Нет ключа homeworks')
                raise KeyError('Нет ключа homeworks')
            logger.error('Тип ключа homeworks не list')
            raise TypeError('Тип ключа homeworks не list')
        logger.error('Значение ключа [homeworks] не список!')
        raise TypeError('Значение ключа [homeworks] не список!')
    except Exception as error:
        logger.error(error)
        raise TypeError(f'Нет ключа, {error}')

response=get_api_answer(1674844256)
r=type(response["homeworks"])
print(r)
