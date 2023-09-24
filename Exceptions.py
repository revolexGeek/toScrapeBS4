class TypeException(Exception):
    """ Возникает при попытке установки неправильного типа данных (Например: нужен Tuple[int, int] получили int"""

    def __init__(self, type1, type2, message=""):
        super().__init__(message)
        self.message = f"Неверено подан тип данных: ожидался {type1}, был получен {type2}."

    def __str__(self):
        return str(self.message)


class ExtensionException(Exception):
    """ Возникает при неверно указанном расширении файла (Например: нужен .xlsx получили .pptx)"""

    def __init__(self, ext1, ext2, message=""):
        super().__init__(message)
        self.message = f"Неверно указано расширение файла: ожидалось {ext1}, было получено {ext2}"

    def __str__(self):
        return str(self.message)


class WrongParamsException(Exception):
    """ Возникает при вводе неверных данных (Например: 1 > 2) """

    def __init__(self, message=""):
        super().__init__(message)
        self.message = f"Неверно введен параметр: {message}! Проверьте правильность ввода."

    def __str__(self):
        return str(self.message)


class FileAlreadyExistsException(Exception):
    """ Возникает когда файл уже существует """

    def __init__(self, filename, message=""):
        super().__init__(message)
        self.message = f"Ошибка! Файл с названием \"{filename}\" уже существует."

    def __str__(self):
        return str(self.message)


if __name__ == '__main__':
    # raise TypeException("1", "2")
    # raise ExtensionException(".xlsx", ".pptx")
    # raise WrongParamsException()
    pass
