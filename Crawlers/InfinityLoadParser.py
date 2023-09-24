import json

from Crawlers.Parser import Parser
from Items import Author, Quote


class InfinityLoadParser(Parser):
    def __init__(self):
        super().__init__()
        self.page: int = 1  # Страница по счету
        self.apiUrl = "http://quotes.toscrape.com/api/quotes"  # Путь к API
        self.json: json = None  # Ответ API

    async def makeRequest(self, link):
        # Делаем задержку
        await self.makeDelay()

        # Отправляем запрос
        print(f"[*] Посылаю запрос с атрибутом page={self.page}.. (#{self.requestCounter})")
        async with self.session.get(link,
                                    params={
                                        "page": self.page
                                    }) as session:
            # Подгружаем JSON массив
            self.json = json.loads(await session.text())

        # Инкрементируем счетчик сделанных запросов
        self.requestCounter += 1

    async def processPage(self):
        for quote in self.json['quotes']:
            # Собираем данные об авторе цитаты
            author = Author(name=quote['author']['name'],
                            bornDate="-",
                            location="-",
                            description="-",
                            link='-')

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

    async def hasNextPage(self):
        if self.json['has_next'] is True or self.json is None:
            return True
        return False

    async def execute(self):
        hasNext = True
        while hasNext:
            await self.makeRequest(self.apiUrl)
            await self.processPage()
            self.page += 1
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
