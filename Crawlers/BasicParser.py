import asyncio

from bs4 import BeautifulSoup
from typing import Tuple

from Crawlers.Parser import Parser
from Items import Author, Quote


class BasicParser(Parser):
    def __init__(self, useAuthorizedSession: bool = False):
        super().__init__()
        self.useAuthorizedSession = useAuthorizedSession
        self.soup = None  # Объект BeautifulSoup

    async def execute(self):
        """
        Точка запуска сбора данных
        :return:
        """
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

    async def renderAuthor(self, link: str) -> Author:
        """
        Сбор данных об авторе
        :param link: Полная ссылка на страницу автора
        :return: Дата рождения автора, локация рождения, описание автора и ссылка на его страницу в виде объекта Author
        """
        soup = await self.makeRequest(link, embedded=False)
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

    async def makeRequest(self, link: str, embedded: bool = True) -> BeautifulSoup:
        """
        Получение веб-страницы
        :param embedded: Заменять ли встроенный объект Soup, или же нет
        :param link: Ссылка на желаемую страницу
        :return:
        """
        # Регулирование задержки
        await self.makeDelay()

        # Послание запроса
        try:
            print(f"[*] Обращаюсь к странице.. (Запросов сделано: {self.requestCounter})")
            async with self.session.get(link) as response:
                source = await response.text()
                self.requestCounter += 1
                soup = BeautifulSoup(source, "lxml")
                if embedded:
                    self.soup = soup
                else:
                    return soup
        except Exception as e:
            print(f"Произошла неопознанная ошибка при запросе к странице. ({link})\n{e}")

    async def isAuthorUnique(self, authorName: str):
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

    async def processPage(self):
        """
        Обработка всех цитат (а также авторов) с одной страницы, которая хранится в self.quotes
        :return: Переходит к следующей странице, если таковая имеется, в другом случае посылает на экспорт в эксель
        """
        for quote in self.soup.findAll("div", class_="quote"):
            # Получение текста цитаты
            text = quote.find("span", class_="text").get_text(strip=True)

            # Получение тэгов цитаты
            tags = list()
            for tag in quote.find("div", class_="tags").findAll("a", class_="tag"):
                tag_text = tag.get_text(strip=True)
                tag_link = self.baseUrl + tag.get("href")
                tags.append(
                    [tag_text, tag_link]
                )

            # Получение информации об авторе цитаты
            authorName = quote.find("small", class_="author").get_text(strip=True)
            author = await self.isAuthorUnique(authorName)
            if author is None:
                authorLink = self.baseUrl + quote.findAll("span")[1].find("a").get("href")
                author = await self.renderAuthor(authorLink)

            # Добавление собранной цитаты в список форматированных цитат
            self.classifiedQuotes.append(
                Quote(
                    text=text,
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


from Crawlers.BasicParser import BasicParser
import asyncio


async def main():
    # Создание экземпляра класса BasicParser
    parser = BasicParser()

    # Запуск сбора данных
    await parser.execute()


if __name__ == "__main__":
    # Получение цикла событий asyncio
    loop = asyncio.get_event_loop()

    # Запуск асинхронной функции main в цикле событий
    loop.run_until_complete(main())
