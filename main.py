import asyncio

from Crawlers.BasicParser import BasicParser
from Crawlers.InfinityLoadParser import InfinityLoadParser
from Crawlers.JSParser import JSParser, JSParserWD


async def generateOrderedList(items: list) -> str:
    """
    Создание нумерованного списка в виде строки
    :param items: список пунктов, которые нужно учесть
    :return: строка, форматированная под нумерованный список
    """
    orderedList = ""
    for h, item in enumerate(items):
        orderedList += f"{h + 1}. {item};\n"

    return orderedList[:-2] + '.\n'


async def getParserDescription(parserClass: str) -> str:
    """
    Вывод краткой информации о выбранном типе парсера
    :param parserClass: наименование класса парсера (parser.__class__.__name__)
    :return: краткое описание
    """

    description = ""

    if parserClass == "BasicParser":
        features = await generateOrderedList(
            [
                'Текст каждой из цитат',
                'Имя автора каждой из цитат',
                'Дату рождения автора каждой из цитат',
                'Место рождения автора каждой из цитат',
                'Описание автора каждой из цитат',
                'Все теги каждой из цитат'
            ]
        )
        description = ("Данный тип парсера предполагает сбор таких данных как:\n"
                       f"{features}"
                       "Данный тип парсера является самым обычным, т.к. при его реализации не возникало никаких\n"
                       "\"подводных камней\".")
    elif parserClass == "InfinityLoadParser":
        features = await generateOrderedList(
            [
                'Текст каждой из цитат',
                'Имени автора каждой из цитат',
                'Все теги каждой из цитат'
            ]
        )
        description = ("Данный тип парсера предполагает сбор таких данных как:\n"
                       f"{features}"
                       "В данном типе парсера используется сбор данных, которые проходят по API сайта при подгрузке\n"
                       "страницы. (Пришлось пройтись Chrome дебагером, чтобы не делать под это WebDriver).")
    elif parserClass == "JSParser":
        features = await generateOrderedList(
            [
                'Текст каждой из цитат',
                'Имени автора каждой из цитат',
                'Все теги каждой из цитат'
            ]
        )
        description = ("Данный тип парсера предполагает сбор таких данных как:\n"
                       f"{features}"
                       "В данном типе парсера происходит утилизация JavaScript кода, который выполняется при\n"
                       "загрузке страницы. Данные берутся методом нахождения правильного <script> тега и\n"
                       "дальнейшего его форматирования в JSON-массив элементов.")
    elif parserClass == "JSParserWD":
        features = await generateOrderedList(
            [
                'Текст каждой из цитат',
                'Имени автора каждой из цитат',
                'Все теги каждой из цитат'
            ]
        )
        description = ("Данный тип парсера предполагает сбор таких данных как:\n"
                       f"{features}"
                       "В данном типе парсера происходит прогрузка JavaScript кода с помощью\n"
                       " использования \"настоящего\" клиента (или же WebDriver'а), зачастую в Headless\n"
                       "(безглавом, без открытия браузера) режиме или же без него.")
    else:
        raise Exception(f"Краткая информация о парсере типа \"{parserClass}\" еще не задана.")

    return description


async def main():
    print("""
     _        _____                          ______  _____    ___ 
    | |      /  ___|                         | ___ \/  ___|  /   |
    | |_ ___ \ `--.  ___ _ __ __ _ _ __   ___| |_/ /\ `--.  / /| |
    | __/ _ \ `--. \/ __| '__/ _` | '_ \ / _ \ ___ \ `--. \/ /_| |
    | || (_) /\__/ / (__| | | (_| | |_) |  __/ |_/ //\__/ /\___  |
     \__\___/\____/ \___|_|  \__,_| .__/ \___\____/ \____/     |_/
                                  | |                             
                                  |_|                             
                            (Made by revolex)
                            github.com/revolex
    """)

    validParser = True
    validNumber = True
    while True:
        print("[Меню]")
        print("1. BasicParser (Микроданные и пагинация)")
        print("2. InfinityLoadParser (Бесконечная прокрутка пагинации)")
        print("3. JSParser (Контент, созданный с помощью JavaScript)")
        print("4. JSParser, delayed=True (Такой же как JSParser, только с задержкой появления)")
        print("5. JSParserWD, WebDriver (JSParser, но с использование WebDriver)")
        print("6. JSParserWD, WebDriver, delayed=True (JSParserWD с использованием задержки)")
        print("7. TablefulParser (Таблица, основанная на беспорядочной компоновке)")
        print("8. AuthParser (Вход в систему с помощью CSRF-токена)")
        print("9. ViewStateParser (Форма фильтрации на основе AJAX с использованием ViewStates)")
        print("10. RandomQuoteParser (Случайные цитаты, с выбором количества отображения)")
        if not validParser:
            print("[!] Данный тип парсера не найден! Пожалуйста, введите существующий номер.")
            validParser = True
        if not validNumber:
            print("[!] Пожалуйста, проверьте правильность ввода! Вы должны ввести число.")
            validNumber = True

        parserType = input("Выбор: ")
        try:
            parserType = int(parserType)
        except ValueError:
            validNumber = False
            continue

        # TODO: Реализовать TablefulParser, AuthParser, ViewStateParser, RandomQuotesParser
        notImpl = NotImplementedError("Выбранный тип парсера на данный момент находится в разработке.")
        parser = None
        if parserType == 1:
            parser = BasicParser()
        elif parserType == 2:
            parser = InfinityLoadParser()
        elif parserType == 3:
            parser = JSParser()
        elif parserType == 4:
            parser = JSParser(delayed=True)
        elif parserType == 5:
            parser = JSParserWD()
        elif parserType == 6:
            parser = JSParserWD(delayed=True)
        elif parserType == 7:
            raise notImpl
        elif parserType == 8:
            raise notImpl
        elif parserType == 9:
            raise notImpl
        elif parserType == 10:
            raise notImpl
        else:
            validParser = False
            continue

        parserClassname = parser.__class__.__name__
        print(f"Вы выбрали {parserType} тип парсера ({parserClassname})!\n")
        print(await getParserDescription(parserClassname))

        # Проверка, асинхронен ли тип парсера (нативный WebDriver не поддерживает асинхронность как таковую)
        if not isinstance(parser, JSParserWD):
            await parser.execute()
        else:
            parser.execute()

        # Выход из While
        break


if __name__ == '__main__':
    # asyncio.run(main())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
