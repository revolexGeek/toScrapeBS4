import asyncio
from typing import Tuple

from bs4 import BeautifulSoup

from Crawlers.Parser import Parser
from Items import Author, Quote


class ViewStateParser(Parser):
    def __init__(self):
        super().__init__()
        self.searchUrl = self.baseUrl + "/search.aspx"
        self.filterUrl = self.baseUrl + "/filter.aspx"
        self.authors: list = list()
        self.tags: list = list()
        self.soup = None

    async def getValidData(self, author: bool = True, tag: bool = False):
        """
        Получаем входные данные для сабмита формы
        :return: Множество, в котором хранятся все авторы, доступные для выбора, а также все теги, доступные для выбора
        """
        # Находим теги <select> в DOM-дереве
        print("[%] Собираю всех возможных авторов и тэги для сбора...")
        authorSelect = None
        tagSelect = None

        if author:
            authorSelect = self.soup.find("select",
                                          {
                                              'name': 'author'
                                          })
        if tag:
            tagSelect = self.soup.find("select",
                                       {
                                           'name': 'tag'
                                       })

        # Собираем данные с тегов <select>
        authors = None
        tags = None
        if authorSelect is not None:
            authors = list()
            for option in authorSelect.findAll("option"):
                optionValue = option.get_text(strip=True)
                if optionValue != '':
                    authors.append(optionValue)

            # authors = [option.get_text(strip=True) for option in authorSelect]

        if tagSelect is not None:
            tags = list()
            for option in tagSelect.findAll("option"):
                optionValue = option.get_text(strip=True)
                if optionValue != '':
                    tags.append(optionValue)

        if authors is not None:
            self.authors = authors[1:]
            print(f"[i] Было собрано: {len(authors)} авторов")
        if tags is not None:
            self.tags = tags[1:]
            print(f"[i] Было собрано: {len(tags)} тегов")

    async def makeRequest(self, link: str, get: bool = True, data: dict = None):
        """
        Создание запроса к странице
        :param link: Ссылка
        :param get: Использовать `GET-запрос` или же `POST-запрос`
        :param data: Задание данных для отправки при использовании `POST-запроса`
        :return: Заполнение `self.soup` полученным HTML кодом страницы
        """
        await self.makeDelay()

        print(f"[*] Делаю запрос к странице {link[26:]}.. (Запрос № {self.requestCounter})")
        if get:
            async with self.session.get(link) as session:
                self.soup = BeautifulSoup(await session.text(), "lxml")
        else:
            if data is None:
                raise Exception("Параметр `data` пуст.")
            print(f"[-] Автор: {data['author']}, тег: {data['tag']}")
            async with self.session.post(link, data=data) as session:
                self.soup = BeautifulSoup(await session.text(), "lxml")

        self.requestCounter += 1

    async def getViewState(self):
        """
        Получение скрытого поля __VIEWSTATE с формы отправки данных
        :return: Значение поля __VIEWSTATE
        """
        print("[*] Получаю __VIEWSTATE формы...")
        viewstate = self.soup.find("form",
                                   {
                                       'name': 'filterform'
                                   }).find("input",
                                           {
                                               'type': 'hidden',
                                               'name': '__VIEWSTATE'
                                           }).get('value')

        print(f"[#] __VIEWSTATE найден! {viewstate[:30]}...")
        return viewstate

    async def processPage(self):
        """
        Сбор цитат со страницы
        :return: Дополняет `self.classifiedQuotes` собранными цитатами
        """
        for quote in self.soup.findAll("div", class_="quote"):
            print("[%] Обрабатываю цитату...")
            text = quote.find("span", class_="content").get_text(strip=True)
            author = Author(
                name=quote.find('span', class_="author").get_text(strip=True),
                bornDate="-",
                location="-",
                description="-",
                link="-"
            )

            tags = [
                [
                    quote.find("span", class_="tag").get_text(strip=True),
                    "-"
                ]
            ]

            self.classifiedQuotes.append(
                Quote(
                    text=text,
                    author=author,
                    tags=tags
                )
            )

    async def getQuotes(self, author: str, tag: str, viewstate: str):
        """
        Сбор цитат по заданным параметрам
        :param author: Имя автора
        :param tag: Интересующий тег
        :param viewstate: Параметр __VIEWSTATE формы
        :return:
        """

        await self.makeRequest(self.filterUrl, get=False,
                               data={
                                   'author': author,
                                   'tag': tag,
                                   'submit_button': 'Search',
                                   '__VIEWSTATE': viewstate
                               })

        await self.processPage()

    async def execute(self):
        """
        Точка запуска сбора данных
        :return:
        """

        # Получаем всех возможных авторов
        await self.makeRequest(self.searchUrl)
        await self.getValidData(author=True, tag=False)

        # Получаем __VIEWSTATE
        viewstate = await self.getViewState()

        # Собираем все цитаты автора по каждому возможному тегу
        for author in self.authors:
            # Посылаем запрос для получения тегов
            await self.makeRequest(self.filterUrl, get=False,
                                   data={
                                       'author': author,
                                       'tag': '----------',
                                       '__VIEWSTATE': viewstate
                                   })

            # Получаем все возможные теги
            await self.getValidData(author=False, tag=True)
            # Итерируемся по каждому возможному тегу
            for tag in self.tags:
                # Обрабатываем страницу
                await self.getQuotes(author, tag, viewstate)

        # Конвертируем собранные данные
        titles = ['Текст цитаты',
                  'Имя автора',
                  'Дата рождения автора',
                  'Локация рождения автора',
                  'Описание автора',
                  'Ссылка на автора',
                  'Тэги',
                  'Ссылки на тэги']
        data = await self.formatQuotes(titles)
        await self.convertToExcel(data[0], data[1])

        # Плавно закрываем объект сессии
        await self.silentQuit()


async def main():
    """
    Проверка работоспособности
    :return:
    """
    parser = ViewStateParser()
    await parser.execute()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
