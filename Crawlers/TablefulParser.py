from bs4 import BeautifulSoup

from Crawlers.Parser import Parser
from Items import Quote, Author


class TablefulParser(Parser):
    def __init__(self):
        super().__init__()
        self.baseUrl: str = "http://quotes.toscrape.com"
        self.currentUrl: str = self.baseUrl + "/tableful"
        self.soup = None

    async def makeRequest(self, link: str):
        print(f"[*] Осуществляю запрос к странице {link}.. (Всего запросов: {self.requestCounter})")
        async with self.session.get(link) as session:
            self.soup = BeautifulSoup(await session.text(), "lxml")
            self.requestCounter += 1

    async def hasNextPage(self) -> bool:
        print("[-] Проверяю, есть ли следующая страница..")
        # Проверяем, есть ли элемент пагинации
        pager = self.soup.find("table").findAll("tr")[-1]

        # Проверяем, есть ли кнопка для перехода на следующую страницу
        if pager is not None:
            pagerButtons = pager.findAll("a")
            if pagerButtons is not None:
                # Отрабатываем возможность пагинации назад и вперед (нам нужно только вперед)
                for button in pagerButtons:
                    if "next" in button.get_text().lower():
                        # Выставляем итерируемую страницу
                        self.currentUrl = self.baseUrl + button.get("href")
                        return True

        # Сообщаем, что следующей страницы нет
        return False

    async def processPage(self):
        """
        Обработка страницы лежащей в self.soup
        :return:
        """

        print("[*] Обрабатываю страницу..")
        # Запоминаем текст цитаты и автора, т.к. не можем их хранить между итерациями
        text = ""
        author = ""
        # with open("index.html", "w+", encoding="UTF-8") as file:
        #     file.write(self.soup.prettify())

        # print(f"table: {self.soup.find('table')}")
        for h, tr in enumerate(self.soup.find("table").findAll("tr")[1:-1]):
            # Исключаем первый row, т.к. это правая панель (топы цитат)
            # Также, исключаем последний row, т.к. это элемент пагинации
            print(f"[%] Обрабатываю Row ({'Четный' if h % 2 == 0 else 'Нечетный'})")
            if h % 2 == 0:
                # Обработка текста
                text = tr.find("td").get_text(strip=True)
                author = text.split("Author: ")[-1]
                text = text.split("Author: ")[0]
            else:
                # Обработка тегов
                tags = list()
                for a in tr.find("td").findAll("a"):
                    tagText = a.get_text(strip=True)
                    tagLink = a.get('href')
                    tags.append(
                        [
                            tagText,
                            self.baseUrl + tagLink
                        ]
                    )

                # Дополняем коллекцию цитат
                self.classifiedQuotes.append(
                    Quote(
                        text=text,
                        author=Author(
                            name=author,
                            bornDate="-",
                            location="-",
                            description="-",
                            link="-"
                        ),
                        tags=tags
                    )
                )

    async def execute(self):
        hasNext = True
        while hasNext:
            await self.makeRequest(self.currentUrl)
            await self.processPage()
            hasNext = await self.hasNextPage()

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
        await self.silentQuit()
