import asyncio

from Crawlers.Parser import Parser
from bs4 import BeautifulSoup

from Items import Author, Quote


class RandomQuoteParser(Parser):
    def __init__(self, toGather: int, sortUnique: bool = False, scrapeAuthors: bool = True):
        super().__init__()
        self.toGather: int = toGather
        self.scrapeAuthors: bool = scrapeAuthors
        self.sortUnique: bool = sortUnique
        self.currentUrl = self.baseUrl + '/random'
        self.soup = None

    async def makeRequest(self, link, embedded: bool = True):
        # Делаем задержку
        await self.makeDelay()

        # Отправляем запрос
        print(f"[*] Посылаю запрос к странице {link[26:]} (#{self.requestCounter})")
        async with self.session.get(link) as session:
            soup = BeautifulSoup(await session.text(), "lxml")
            if embedded:
                self.soup = soup
            else:
                self.requestCounter += 1
                return soup

        # Инкрементируем счетчик сделанных запросов
        self.requestCounter += 1

    async def isAuthorUnique(self, authorLink: str):
        """
        Проверка автора на уникальность
        :param authorLink: имя автора
        :return: True - если автор не уникален, в обратном случае - инстанс класса Author
        """

        for quote in self.classifiedQuotes:
            if quote.author.link == authorLink:
                print("[*] Автор уже был собран, пропускаю!")
                return Author

        return True

    async def isQuoteUnique(self, quoteToCompare: Quote) -> bool:
        """
        Проверка цитаты на уникальность
        :param quoteToCompare: цитата, которую нужно проверить
        :return: True - в случае, если цитата является уникальной, False - в обратном
        """
        for quote in self.classifiedQuotes:
            if quote == quoteToCompare:
                print("[*] Данная цитата уже была собрана.")
                return False

        return True

    async def processAuthor(self, link):
        """
        Сбор подробных данных об авторе
        :param link: ссылка на страницу об авторе
        :return: заполненный объект `Author`
        """
        soup = await self.makeRequest(link, embedded=False)
        name = soup.find("h3", class_="author-title").get_text(strip=True)
        bornDate = soup.find("span", class_="author-born-date").get_text(strip=True)
        location = soup.find("span", class_="author-born-location").get_text(strip=True)
        description = soup.find("div", class_="author-description").get_text(strip=True)

        return Author(
            name=name,
            description=description,
            location=location,
            bornDate=bornDate,
            link=link
        )

    async def processPage(self):
        # Ищем элемент цитаты
        quote = self.soup.find("div", class_="quote")

        # Собираем текст
        text = quote.find("span", class_="text").get_text(strip=True)

        # Собираем автора
        author = None
        authorName = quote.find("small", class_="author").get_text(strip=True)
        authorLink = self.baseUrl + quote.find("a").get('href')

        # Если нужно собирать полную информацию об авторе
        if self.scrapeAuthors:
            # Проверка на уникальность
            author = await self.isAuthorUnique(authorLink)
            if author:
                author = await self.processAuthor(authorLink)
        else:
            author = Author(
                name=authorName,
                bornDate="-",
                location="-",
                description="-",
                link=self.baseUrl + quote.find("a").get('href')
            )

        # Собираем теги
        tags = list()
        for tag in quote.find('div', class_='tags').findAll("a", class_="tag"):
            tags.append(
                [
                    tag.get_text(strip=True),
                    tag.get('href')
                ]
            )

        # Выстраиваем объект Quote
        resultQuote = Quote(
            text=text,
            author=author,
            tags=tags
        )

        # Дополняем список цитат
        if self.sortUnique:
            # Проверяем на уникальность
            if await self.isQuoteUnique(resultQuote):
                self.classifiedQuotes.append(resultQuote)
        else:
            self.classifiedQuotes.append(resultQuote)

    async def execute(self):
        # Итерируемся `toGater` раз
        for h in range(self.toGather):
            await self.makeRequest(self.currentUrl)
            await self.processPage()

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
    Тестирование
    :return:
    """

    parser = RandomQuoteParser(50, sortUnique=False)
    await parser.execute()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
