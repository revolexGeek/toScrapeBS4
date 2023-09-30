import asyncio
from bs4 import BeautifulSoup
from aiohttp import ClientSession


class AuthManager:
    def __init__(self, username: str = "revolex", password: str = "qwerty123"):
        self.username = username
        self.password = password
        self.session = ClientSession()
        if not isinstance(self.session, ClientSession):
            raise Exception(f"На вход получен не объект ClientSession, а {type(self.session)}.")
        self.baseUrl = "http://quotes.toscrape.com/login"
        self.soup = None

    async def makeRequest(self, link: str, get: bool = True, data: dict = None):
        """
        Отправка запроса к веб-странице
        :param link: Ссылка
        :param get: Использовать GET или же POST запрос
        :param data: Данные для отправки при помощи POST запроса
        :return: self.soup
        """
        if get:
            async with self.session.get(link) as session:
                self.soup = BeautifulSoup(await session.text(), "lxml")
        else:
            if data is None:
                raise Exception("Словарь посылаемых данных пуст.")

            async with self.session.post(link, data=data, headers={'Referrer': self.baseUrl}) as session:
                self.soup = BeautifulSoup(await session.text(), "lxml")

    async def getCSRF(self) -> str:
        """
        Получение CSRF-токена из формы входа
        :return: значение CSRF-токена
        """
        print("[AuthManager] -> Получаю CSRF-Токен..")
        await self.makeRequest(self.baseUrl)
        return self.soup.find("form",
                              {
                                  'action': '/login'
                              }
                              ).find("input",
                                     {
                                         'type': 'hidden',
                                         'name': 'csrf_token'
                                     }
                                     ).get('value')

    async def login(self):
        print("[AuthManager] -> Произвожу попытку входа..")
        await self.makeRequest(self.baseUrl, get=False, data={
            'csrf_token': await self.getCSRF(),
            'username': self.username,
            'password': self.password
        })

    async def isLoggedIn(self) -> bool:
        """
        Проверка, произведен ли вход в систему
        :return: True/False
        """
        print("[AuthManager] -> Проверяю состояние входа в систему.. ")
        links = self.soup.findAll("a")
        for a in links:
            if a.has_attr("href"):
                if 'logout' in a.get('href'):
                    print("[AuthManager] -> Вход произведен успешно! (Сессия авторизована)")
                    return True

        print("[AuthManager] -> Произошла ошибка входа.. (Сессия не авторизована)")
        return False

    async def quit(self):
        """
        Закрытие объекта ClientSession
        :return:
        """
        if not self.session.closed:
            await self.session.close()

    async def getAuthorizedSession(self):
        """
        Получение объекта авторизованной сессии
        :return: авторизованная ClientSession
        """
        print("[AuthManager] -> Начинаю получение авторизованной сессии..")
        await self.login()

        if await self.isLoggedIn():
            return self.session
        else:
            raise Exception("Произошла ошибка при попытке входа в систему.")


async def main():
    """
    Тестирование AuthManager
    :return:
    """
    cManager = AuthManager()
    await cManager.makeRequest("http://quotes.toscrape.com")
    await cManager.isLoggedIn()
    session = await cManager.getAuthorizedSession()
    await cManager.quit()

    """
    Output:

    [AuthManager] -> Проверяю состояние входа в систему.. 
    [AuthManager] -> Произошла ошибка входа.. (Сессия не авторизована)
    [AuthManager] -> Начинаю получение авторизованной сессии..
    [AuthManager] -> Произвожу попытку входа..
    [AuthManager] -> Получаю CSRF-Токен..
    [AuthManager] -> Проверяю состояние входа в систему.. 
    [AuthManager] -> Вход произведен успешно! (Сессия авторизована)
    """


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
