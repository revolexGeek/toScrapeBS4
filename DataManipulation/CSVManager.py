import csv
import os


class CSVManager:
    def __init__(self, outputFilename: str = "output.csv"):
        self.outputFilename = outputFilename  # Название выходного файла
        self.setOutputFilename(outputFilename)

    def fillCSV(self, titles: list, data: list):
        """
        Заполнение Excel файла
        :param titles: Список заголовков
        :param data: Список данных, которые должны стоять под заголовками
        :return: Заполняет внутреннюю переменную self.sheet
        """

        """
        Структура входных данных

        titles: list = [
            'title1',
            'title2',
            ...
        ]

        data: list = [
            [
                'item1',
                'item2',
                'item3',
                'item4',
                ...
            ],
            [
                'item1',
                'item2',
                'item3',
                'item4',
                ...
            ],
            ...
        ]
        """

        # Определение максимального алфавита столбцов
        # alphabet = ascii_uppercase[:len(titles)]

        # Заполнение заголовков
        while True:
            try:
                with open(self.outputFilename, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(titles)
                    break
            except PermissionError:
                print("Произошла ошибка записи данных!\nПопробуйте закрыть его и повторить попытку.")
                input("[X] Нажмите Enter чтобы повторить попытку..")

        # Заполнение строчек данными
        while True:
            try:
                with open(self.outputFilename, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    for item in data:
                        writer.writerow(item)
                    break
            except PermissionError:
                print("Произошла ошибка записи данных!\nПопробуйте закрыть его и повторить попытку.")
                input("[X] Нажмите Enter чтобы повторить попытку..")


    def setOutputFilename(self, filename: str):
        """
        Проверка правильности ввода имени выходного файла.
        :param filename: Имя файла.
        :return: Если данные введены корректно - имя выходного файла.
        """
        newName = False
        if isinstance(filename, str):
            while True:
                if newName:
                    filename = input("Выберите новое имя файла: ")
                    newName = False
                if filename.endswith(".csv") and len(filename.strip()) > 4:
                    if os.path.isfile(filename):
                        print(f"[%] Файл с таким названием ({self.outputFilename}) уже существует.")
                        rewrite = input("Перезаписать? (+/-): ")
                        if rewrite == "+":
                            print("[*] Файл будет перезаписан.")
                            while True:
                                try:
                                    os.remove(filename)
                                    break
                                except PermissionError:
                                    print("[!] Возникла ошибка!\n"
                                          "Необходимо закрыть этот CSV документ перед его перезаписыванием.")
                                    input("Нажмите Enter чтобы попробовать еще раз..")
                            self.outputFilename = filename
                            break
                        elif rewrite == "-":
                            newName = True
                        else:
                            print("[!] Команда не распознана.")
                    else:
                        break
                else:
                    print("[!] Неверно указано название файла. Пример: out.csv")
                    newName = True

            self.outputFilename = filename
            print("[*] Выходной файл установлен успешно. ")


if __name__ == '__main__':
    # Пример использования
    csvMan = CSVManager(outputFilename="out.csv")
    titles = ['title1', 'title2', 'title3']
    data = [
        ['data1', 'data2', 'data3'],
        ['data4', 'data5', 'data6'],
        ['data7', 'data8', 'data9']
    ]

    csvMan.fillCSV(titles, data)
