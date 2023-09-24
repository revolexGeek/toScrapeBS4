import random
from typing import Tuple

import asyncio
from aiohttp import ClientSession
import time

from DataManipulation.ExcelManager import ExcelManager
from Exceptions import TypeException, WrongParamsException


class Parser:
    def __init__(self):
        self.delay = (0, 0)  # Задержка между запросами
        self.baseUrl: str = "http://quotes.toscrape.com"  # Базовая ссылка
        self.currentUrl: str = self.baseUrl  # Итерируемая ссылка
        self.session: ClientSession = ClientSession()  # Объект сессии
        self.classifiedQuotes: list = list()  # Собранные цитаты в виде класса 'Quote'
        self.requestCounter = 0  # Количество сделанных запросов
        self.startTime = time.time()  # Время начала работы программы
        self.endTime = None  # Время конца работы программы

    async def execute(self):
        """
        Точка запуска сбора данных
        :return:
        """
        pass

    async def calculateWorkTime(self):
        self.endTime = time.time()
        return round(self.endTime - self.startTime, 2)

    async def getRandomDelay(self) -> int:
        """
        Получение случайной задержки (в секундах) между выбранными значениями self.delay
        :return: Случайное число - количество секунд задержки
        """
        return random.randint(self.delay[0], self.delay[1])

    async def makeDelay(self):
        """
        Создание задержки между запросами
        :return:
        """
        if self.delay[0] != 0 or self.delay[1] != 0:
            randInt = await self.getRandomDelay()
            print(f"[#] Задержка в {randInt} секунд..")
            await asyncio.sleep(randInt)

    async def makeRequest(self, link: str):
        """
        Создание запроса к странице
        :param link:
        :return:
        """
        pass

    async def formatQuotes(self, titles: list) -> Tuple[list, list]:
        """
        Преобразование self.classifiedQuotes в два списка для экспорта при помощи ExcelManager
        :return: Двумерный кортеж состоящий из списка заголовков и списка построчно-заполняемых данных
        """
        formatedQuotes = list()
        for quote in self.classifiedQuotes:
            temp = list()
            temp.append(quote.text)
            temp.append(quote.author.name)
            temp.append(quote.author.bornDate)
            temp.append(quote.author.location)
            temp.append(quote.author.description)
            temp.append(quote.author.link)
            temp.append(quote.getTagsString(isText=True))
            temp.append(quote.getTagsString(isText=False))

            formatedQuotes.append(temp)

        return titles, formatedQuotes

    def setDelay(self, delay: Tuple[int, int]):
        """
        Проверка на правильность ввода задержки между запросами.
        :param delay: Кортеж двух чисел: минимальной задержки и максимальной задержки.
        :return: Если данные введены в нужном формате - исходный кортеж.
        """
        newDelay = False
        while True:
            try:
                if newDelay:
                    try:
                        delay = tuple(map(int, input("Введите задержку: (Например: 0,5): ").split(',')))
                        newDelay = False
                    except Exception:
                        print("[!] Ошибка ввода! Пример: 0,5.")
                if isinstance(delay, Tuple):
                    if len(delay) == 2 and (isinstance(delay[0], int) and isinstance(delay[1], int)):
                        left_range = delay[0]
                        right_range = delay[1]
                        if left_range > right_range:
                            # print("Минимальная задержка не может быть больше максимальной!")
                            raise WrongParamsException("Минимальная задержка не может быть больше максимальной")
                        elif right_range < left_range:
                            # print("Максимальная задержка не может быть больше минимальной!")
                            raise WrongParamsException("Максимальная задержка не может быть больше минимальной")
                        else:
                            if left_range == right_range:
                                print(f"[%] Установлена статическая задержка запросов: "
                                      f"{left_range} секунд.")
                            else:
                                print(f"[%] Установлена динамическая задержка запросов: "
                                      f"от {left_range} до {right_range} секунд.")
                            return delay
                    else:
                        raise WrongParamsException()
                else:
                    raise TypeException(type(Tuple[int, int]), type(delay))
            except WrongParamsException as wpe:
                print(wpe)
                newDelay = True
            except TypeException as te:
                print(te)
                newDelay = True

    async def processPage(self):
        """
        Обработка страницы
        :return:
        """
        pass

    async def hasNextPage(self) -> bool:
        """
        Проверка существования следующей страницы
        :return:
        """
        pass

    async def silentQuit(self):
        """
        Тихий выход из программы
        :return:
        """
        print("[*] Работа завершена.")
        print(f"[i] Было собрано: {len(self.classifiedQuotes)} цитат.")
        workingTime = await self.calculateWorkTime()
        print(f"[i] Программа завершила работа за: {workingTime} секунд.")
        if self.session is not None and not self.session.closed:
            await self.session.close()

    async def convertToExcel(self, titles, data):
        """
        Конвертирование собранных данных в Excel
        :param titles: Список заголовков
        :param data: Список собранных данных (построчно)
        :return:
        """
        excelMan = ExcelManager()
        excelMan.fillSheet(titles, data)
        excelMan.save()
