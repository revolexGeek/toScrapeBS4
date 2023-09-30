import json
import time
from typing import Tuple

from bs4 import BeautifulSoup

from Crawlers.Parser import Parser
from DataManipulation.ExcelManager import ExcelManager
from Items import Author, Quote

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class JSParser(Parser):
    def __init__(self, delayed: bool = False, useAuthorizedSession: bool = False):
        super().__init__()
        self.delayed = delayed
        self.useAuthorizedSession = useAuthorizedSession
        self.baseUrl = "http://quotes.toscrape.com"  # стартовая ссылка
        self.soup = None  # Объект BeautifulSoup
        self.currentUrl = self.baseUrl + "/js" if not self.delayed else self.baseUrl + "/js-delayed"  # Итерируемая ссылка

    async def execute(self):
        if self.useAuthorizedSession:
            await self.authorizeSession()

        isNextPageExists = True
        while isNextPageExists:
            await self.makeRequest(self.currentUrl)
            await self.processPage()
            isNextPageExists = await self.hasNextPage()

        titles = ['Текст цитаты',
                  'Имя автора',
                  'Дата рождения автора',
                  'Локация рождения автора',
                  'Описание автора',
                  'Ссылка на автора',
                  'Тэги',
                  'Ссылки на тэги']

        formattedData = await self.formatQuotes(titles)
        await self.convertToExcel(formattedData[0], formattedData[1])
        await self.silentQuit()

    async def makeRequest(self, link: str, embedded: bool = True):
        await self.makeDelay()
        try:
            print(f"[*] Посылаю запрос к \"{link[26:]}\" (Запрос № {self.requestCounter})")
            async with self.session.get(link) as response:
                soup = BeautifulSoup(await response.text(), "lxml")
                self.requestCounter += 1
                if embedded:
                    self.soup = soup
                else:
                    return soup
        except Exception as e:
            print(f"[!] Произошла необработанная ошибка при попытке запроса к странице! {e}.")

    async def processPage(self):
        # Нахождение исполняемого при заходе JS-скрипта
        appendScript = None
        for script in self.soup.findAll("script"):
            if "var" in script.text:
                appendScript = script.text

        # Дебаг, в случае не нахождения нужного исполняемого скрипта
        # if appendScript is None:
        #     with open("index.html", "w+", encoding="utf-8") as file:
        #         file.write(self.soup.prettify)

        # Изъятие JSON-массива из скрипта
        data = await self.extractDataFromScript(appendScript)
        for quote in data:
            # Собираем данные об авторе цитаты
            author = Author(
                name=quote['author']['name'],
                bornDate="-",
                location="-",
                description="-",
                link="-"
            )

            # Собираем тэги
            tags = list()
            for tag in quote['tags']:
                tags.append(
                    [tag, "-"]
                )

            # Дополняем хранилище цитат
            self.classifiedQuotes.append(
                Quote(
                    text=quote['text'],
                    author=author,
                    tags=tags
                )
            )

    async def hasNextPage(self) -> bool:
        """
        Переход к следующей странице, если таковая имеется
        :return: "True" если следующая страница существует, "False" в обратном случае
        """
        if self.soup is None:
            return True

        pager = self.soup.find("li", class_="next")
        if pager is not None:
            pager = pager.find("a").get("href")
            self.currentUrl = self.baseUrl + pager
            return True
        return False

    async def extractDataFromScript(self, scriptText: str) -> json:
        """
        Конвертирование скрипта с данными со странцы в массив JSON-элементов
        :param scriptText: Текст нужной* части скрипта (*часть, которая содержит данные)
        :return: Массив json-элементов
        """
        if not self.delayed:
            scriptText = scriptText.replace("var data = ", "")
            scriptText = scriptText.rsplit("];", 2)
            scriptText = scriptText[0]
            scriptText += "]"
        else:
            scriptText = scriptText.split('{', 1)[1]
            scriptText = scriptText.replace("var data = ", "")
            scriptText = scriptText.rsplit("];", 2)
            scriptText = scriptText[0]
            scriptText += "]"

        return json.loads(scriptText)


class JSParserWD:
    def __init__(self, delayed: bool = False, headless: bool = True):
        super().__init__()
        self.delayed: bool = delayed
        self.baseUrl: str = "http://quotes.toscrape.com"  # Стартовая ссылка
        self.currentUrl: str = self.baseUrl + "/js"\
            if not self.delayed\
            else self.baseUrl + "/js-delayed"  # Итерируемая ссылка
        self.driver: uc.Chrome = uc.Chrome(headless=headless, use_subprocess=True, version_main=116)  # WebDriver
        self.classifiedQuotes: list = list()  # Цитаты, выраженные в объектах типа 'Quote'
        self.startTime = time.time()  # Время начала работы программы
        self.endTime = None  # Время конца работы программы

    def execute(self):
        """
        Точка запуска сбора данных
        :return:
        """

        # Итерируемся по всем страницам веб-приложения
        isNextPageExists = True
        self.makeRequest(self.currentUrl)
        while isNextPageExists:
            # self.makeRequest(self.currentUrl)
            self.processPage()
            isNextPageExists = self.hasNextPage()

        # Конвертируем собранную информацию в Excel файл
        titles = ['Текст цитаты',
                  'Имя автора',
                  'Дата рождения автора',
                  'Локация рождения автора',
                  'Описание автора',
                  'Ссылка на автора',
                  'Тэги',
                  'Ссылки на тэги']

        formattedData = self.formatQuotes(titles)
        self.convertToExcel(formattedData[0], formattedData[1])

        # Завершаем выполнение программы
        self.silentQuit()

    def formatQuotes(self, titles: list) -> Tuple[list, list]:
        """
        Преобразование self.classifiedQuotes в два списка для экспорта при помощи ExcelManager
        :return: Двумерный кортеж состоящий из списка заголовков и списка построчно-заполняемых данных
        """
        formattedQuotes = list()
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

            formattedQuotes.append(temp)

        return titles, formattedQuotes

    @staticmethod
    def convertToExcel(titles, data):
        """
        Конвертирование собранных данных в Excel
        :param titles: Список заголовков
        :param data: Список собранных данных (построчно)
        :return:
        """
        print("[%] Создаю Excel документ..")
        excelMan = ExcelManager()
        excelMan.fillSheet(titles, data)
        excelMan.save()

    def makeRequest(self, link: str):
        """
        Направление объекта Driver, открытие ссылок
        :param link: Ссылка, к которой необходимо обратится
        :return:
        """
        print(f"[*] Делаю запрос к {link}...")
        self.driver.get(link)

    def hasNextPage(self) -> bool:
        """
        Переход к следующей странице, если таковая имеется
        :return: "True" если следующая страница существует, "False" в обратном случае
        """
        # Скорее всего можно упростить!
        print("[%] Проверяю, есть ли следующая страница..")
        pager = self.driver.find_element(By.XPATH, "/html/body/div/nav/ul")
        if pager is not None:
            nextButton = pager.find_elements(By.TAG_NAME, "li")
            if len(nextButton) == 2:
                if nextButton[0].get_attribute("class") == "next":
                    nextButton = nextButton[0]
                else:
                    nextButton = nextButton[1]
            elif len(nextButton) == 1:
                if not nextButton[0].get_attribute("class") == "next":
                    return False
                else:
                    nextButton = nextButton[0]

            if nextButton is not None:
                print("[*] Следующая страница найдена. Произвожу переход!")
                nextButton.find_element(By.CSS_SELECTOR, "a").click()
                return True
            else:
                return False
        return False

    def processPage(self):
        """
        Обработка текущей страницы
        :return:
        """
        if self.delayed:
            # Ожидание WebElement в DOM дереве, с таймаутом 20 секунд
            print("[%] Ожидаю появление элемента в DOM-дереве..")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))
        for quote in self.driver.find_elements(By.CSS_SELECTOR, "div.quote"):
            # Обработка всех цитат, представленных на странице
            print("[%] Обрабатываю цитаты на текущей странице..")
            text = quote.find_element(By.CSS_SELECTOR, "span.text").text
            author = Author(
                name=quote.find_element(By.CSS_SELECTOR, "small.author").text,
                bornDate="-",
                location="-",
                description="-",
                link="-"
            )

            # Сбор тэгов
            tags = list()
            for tag in quote.find_elements(By.CSS_SELECTOR, "a.tag"):
                tags.append(
                    [tag.text, "-"]
                )

            # Дополнение коллекции собранных цитат
            self.classifiedQuotes.append(
                Quote(
                    text=text,
                    author=author,
                    tags=tags
                )
            )

    def calculateWorkTime(self) -> float:
        """
        Рассчет времени работы программы
        :return: Число - время работы программы в секундах
        """
        self.endTime = time.time()
        return round(self.endTime - self.startTime, 2)

    def silentQuit(self):
        """
        Тихий выход из программы
        :return:
        """
        print("[*] Работа завершена.")
        print(f"[i] Было собрано: {len(self.classifiedQuotes)} цитат.")
        workingTime = self.calculateWorkTime()
        print(f"[i] Программа завершила работа за: {workingTime} секунд.")
        self.killDriver()

    def killDriver(self):
        """
        Убить (завершить) выполнение объекта WebDriver
        :return:
        """
        if self.driver.service.is_connectable():
            print("[X] Завершаю работу WebDriver'а...")
            self.driver.quit()

    def __del__(self):
        """
        При удалении экземпляра класса, проверка на закрытость WebDriver'а, чтобы не наплодить миллион копий при
        дебаге
        :return:
        """
        self.killDriver()
