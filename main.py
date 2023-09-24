import asyncio

from Crawlers.BasicParser import BasicParser
from Crawlers.InfinityLoadParser import InfinityLoadParser
from Crawlers.JSParser import JSParser, JSParserWD


# outFname = input("Введите имя выходного файла (output.xlsx): ")
# while True:
#     try:
#         delay = tuple(map(int, input("Введите задержку в секундах (0,5): ").split(',')))
#         if len(delay) == 2:
#             break
#     except Exception:
#         print("[!] Данные указаны в неправильном формате. Пример: 0,5.")
#
# parser = Parser(outputFilename=outFname, delay=delay)
# parser.execute

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
                            (Mady by revolex)
                            github.com/revolex
    """)

    while True:
        print("[Меню]")
        print("1. BasicParser (Микроданные и пагинация)")
        print("2. InfinityLoadParser (Бесконечная прокрутка пагинации)")
        print("3. JSParser (Контент, созданный с помощью JavaScript)")
        print("4. JSParser, delayed=True (Такой же как выше, только с задержкой появления)")
        print("5. JSParserWD, WebDriver (Вышеупомянутые, но с использование WebDriver)")
        print("6. JSParserWD, WebDriver, delayed=True (Вышеупомянутые, но с использование WebDriver и задержки)")
        print("7. TablefulParser (Таблица, основанная на беспорядочной компоновке)")
        print("8. AuthParser (Вход в систему с помощью CSRF-токена)")
        print("9. ViewStateParser (Форма фильтрации на основе AJAX с использованием ViewStates)")
        print("10. RandomQuoteParser (Случайные цитаты, с выбором количества отображения)")

        ask = input("Выбор: ")
        try:
            ask = int(ask)
        except ValueError:
            print("Введите число!")
            continue

        parser = None
        if ask == 1:
            parser = BasicParser()
        elif ask == 2:
            parser = InfinityLoadParser()
        elif ask == 3:
            parser = JSParser()
        elif ask == 4:
            parser = JSParser(delayed=True)
        elif ask == 5:
            parser = JSParserWD()
        elif ask == 6:
            parser = JSParserWD(delayed=True)
        elif ask == 7:
            continue
        elif ask == 8:
            continue
        elif ask == 9:
            continue
        elif ask == 10:
            continue
        else:
            print("[!] Данный тип парсера не найден! Пожалуйста, введите существующий номер.")
            continue

        if not isinstance(parser, JSParserWD):
            await parser.execute()
        else:
            parser.execute()

        break


if __name__ == '__main__':
    # asyncio.run(main())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
