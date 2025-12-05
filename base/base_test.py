import requests


class BaseTest:
    """Базовый класс для всех тестов API"""

    BASE_URL = "https://petstore.swagger.io/v2"
    TIMEOUT = 10

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })