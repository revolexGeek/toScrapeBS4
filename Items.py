class Tag:
    def __init__(self, text, link):
        self.text = text
        self.link = link

    def getArrayed(self):
        return [
            self.text,
            self.link
        ]

    def __repr__(self):
        return "<Tag {}>".format(self.text)


class Author:
    def __init__(self, name, bornDate, location, description, link):
        self.name = name
        self.bornDate = bornDate
        self.location = location
        self.description = description
        self.link = link

    def getArrayed(self):
        return [
            self.name,
            self.bornDate,
            self.location,
            self.description,
            self.link
        ]

    def __repr__(self):
        return "<Author {}>".format(self.name)


class Quote:
    def __init__(self, text: str, author: Author, tags: list):
        self.text = text
        self.author = author
        self.tags = tags
        self.formatTagsIntoObjects()

    def formatTagsIntoObjects(self):
        temp = list()
        for tag in self.tags:
            temp.append(Tag(
                tag[0],
                tag[1]
            ))

        self.tags = temp

    def getTagsString(self, isText: bool = True, separator: str = ";", end: str = ".") -> str:
        """
        Конвертирование тегов из объектов в строку
        :param isText: Преобразовать текст тэгов, или же ссылки на тэги
        :param separator: Разделяющий символ
        :param end: Конечный символ
        :return: Форматированная строга тэгов
        """
        tags_list = list()
        for tag in self.tags:
            tags_list.append(tag.text if isText else tag.link)

        return separator.join(tags_list)[:-1] + end if len(tags_list) != 0 else "-"

    def getArrayed(self):
        return [
            self.text,
            self.author,
            self.tags
        ]

    def __repr__(self):
        return "<Quote {}>".format(self.text[:10])


if __name__ == '__main__':
    # Пример использования
    author = Author("Evan",
                    "12/01/2004",
                    "Murmansk",
                    "Description",
                    "https://quotes.toscrape.com/author/Evan")
    tags = [
        ['Cloudy', "https://quotes.toscrape.com/tag/cloudy"],
        ['Evening', "https://quotes.toscrape.com/tag/evening"]
    ]
    quote = Quote(text="Quote's text.",
                  author=author,
                  tags=tags)

    # Вывод информации
    print(quote.text)
    print(quote.author.getArrayed())
    print(quote.tags)

    """
    Вывод:
    
    Quote's text.
    ['Evan', '12/01/2004', 'Murmansk', 'Description', 'https://quotes.toscrape.com/author/Evan']
    [<Tag Cloudy>, <Tag Evening>]
    """
