import random
from time import sleep
import requests
from bs4 import BeautifulSoup
from typing import Tuple

from DataManipulation.ExcelManager import ExcelManager
from Exceptions import TypeException, WrongParamsException
from Items import Author, Quote


# TODO: add multithreading or asynchronous support.
class Parser:
    def __init__(self, outputFilename: str = "BasicParserOutput.xlsx", delay: Tuple[int, int] = (0, 0)):
        self.delay = delay  # Время задержки между запросами
        self.setDelay(delay)
        self.base_url: str = "http://quotes.toscrape.com"  # Изначальная ссылка (константа)
        self.current_url: str = self.base_url  # Итерируемая ссылка
        self.session = requests.session()  # Объект сессии для создания запросов
        self.quotes = None  # Список цитат на итерируемой странице
        self.classifiedQuotes = list()
        self.soup = None  # Объект BeautifulSoup
        self.requestsMade = 0  # Количество отправленных запросов

        sleep(3)

    def execute(self):
        """
        Точка запуска сбора данных
        :return:
        """
        self.parsePage()

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

    def renderAuthor(self, link: str) -> Author:
        """
        Сбор данных об авторе
        :param link: Полная ссылка на страницу автора
        :return: Дата рождения автора, локация рождения, описание автора и ссылка на его страницу в виде объекта Author
        """
        soup = self.makeRequest(link, embedded=False)
        print(f"[-] Собираю данные об авторе.. ({link[34:].replace('-', ' ')})")
        author_name = soup.find("h3", class_="author-title").get_text(strip=True)
        author_born = soup.find("span", class_="author-born-date").get_text(strip=True)
        author_city = soup.find("span", class_="author-born-location").get_text(strip=True)
        author_description = soup.find("div", class_="author-description").get_text(strip=True)
        return Author(author_name,
                      author_born,
                      author_city,
                      author_description,
                      link)

    def makeRequest(self, link: str, embedded: bool = True) -> BeautifulSoup:
        """
        Получение веб-страницы
        :param embedded: Заменять ли встроенный объект Soup, или же нет
        :param link: Ссылка на желаемую страницу
        :return:
        """
        # Регулирование задержки
        if self.delay[0] != 0 or self.delay[1] != 0:
            randInt = random.randint(self.delay[0], self.delay[1])
            print(f"[#] Задержка в {randInt} секунд..")
            sleep(randInt)

        # Послание запроса
        try:
            print(f"[*] Обращаюсь к странице.. (Запросов сделано: {self.requestsMade})")
            response = self.session.get(link)
            if response.status_code == 200:
                print("[*] Получен ответ: 200")
                self.requestsMade += 1
                soup = BeautifulSoup(response.text, "lxml")
                if embedded:
                    self.soup = BeautifulSoup(response.text, "lxml")
                else:
                    return soup
            else:
                print(f"Не удалось получить страницу ({link}). Получен ответ: {response.status_code}.")
        except Exception as e:
            print(f"Произошла неопознанная ошибка при запросе к странице. ({link})\n{e}")

    def isAuthorUnique(self, authorName: str):
        """
        Проверка на уникальность автора
        :param authorName: Имя автора
        :return: Объект автора, если он уже был собран, в ином случае None
        """
        for quote in self.classifiedQuotes:
            if quote.author.name == authorName:
                print(f"[*] Автор {authorName} уже был собран! Пропускаю..")
                return quote.author

        return None

    def renderQuotes(self):
        """
        Обработка всех цитат (а также авторов) с одной страницы, которая хранится в self.quotes
        :return: Переходит к следующей странице, если таковая имеется, в другом случае посылает на экспорт в эксель
        """
        for quote in self.quotes:
            # Получение текста цитаты
            text = quote.find("span", class_="text").get_text(strip=True)

            # Получение тэгов цитаты
            tags = list()
            for tag in quote.find("div", class_="tags").findAll("a", class_="tag"):
                tag_text = tag.get_text(strip=True)
                tag_link = self.base_url + tag.get("href")
                tags.append(
                    [tag_text, tag_link]
                )

            # Получение информации об авторе цитаты
            authorName = quote.find("small", class_="author").get_text(strip=True)
            author = self.isAuthorUnique(authorName)
            if author is None:
                authorLink = self.base_url + quote.findAll("span")[1].find("a").get("href")
                author = self.renderAuthor(authorLink)

            # Добавление собранной цитаты в список форматированных цитат
            self.classifiedQuotes.append(
                Quote(
                    text=text,
                    author=author,
                    tags=tags
                )
            )

        # Если это последняя страница
        if not self.gotoNextPageIfExists():
            # Сохранение собранных данных
            ExcelMan = ExcelManager()

            # Текст цитаты, имя автора, дата рождения автора, локация рождения автора, описание автора, ссылка на автора, тэги, ссылки на теги
            titles = ['Текст цитаты',
                      'Имя автора',
                      'Дата рождения автора',
                      'Локация рождения автора',
                      'Описание автора',
                      'Ссылка на автора',
                      'Тэги',
                      'Ссылки на тэги']

            resultData = list()
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

                resultData.append(temp)

            ExcelMan.fillSheet(titles, resultData)

            ExcelMan.save()

            self.informAndExit()

    def parsePage(self):
        """
        Сбор цитат со страницы
        :return: После успешного сбора, переходит к обработке собранных цитат
        """
        self.makeRequest(self.current_url)
        self.quotes = [a for a in self.soup.findAll("div", class_="quote")]
        self.renderQuotes()

    def gotoNextPageIfExists(self):
        """
        Переход к следующей странице, если таковая имеется
        :return: "True" если следующая страница существует, "False" в обратном случае
        """
        self.makeRequest(self.current_url)
        pager = self.soup.find("li", class_="next")
        if pager is not None:
            pager = pager.find("a").get("href")
            self.current_url = self.base_url + pager
            self.session.get(self.current_url + pager)
            self.parsePage()
            return True
        else:
            return False

    def informAndExit(self):
        """
        Мягкий выход из программы
        :return: Количество собранных цитат.
        """
        print("[*] Парсер закончил работу.\n"
              f" ┗ Было собрано: {len(self.classifiedQuotes)} цитат.")
        input("\n[X] Нажмите Enter чтобы выйти..")
