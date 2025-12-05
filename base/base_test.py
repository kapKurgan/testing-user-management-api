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

    def _make_request(
            self,
            method: str,
            endpoint: str,
            data=None,
            params=None,
            expected_status: int = 200
    ) -> requests.Response:
        """Универсальный метод для выполнения HTTP-запросов"""
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(
            method=method.upper(),
            url=url,
            json=data,
            params=params,
            timeout=self.TIMEOUT
        )
        response.raise_for_status()
        return response

    def create_user(self, user_data): return self._make_request("POST", "/user", data=user_data)

    def get_user(self, username): return self._make_request("GET", f"/user/{username}")

    def update_user(self, username, user_data): return self._make_request("PUT", f"/user/{username}", data=user_data)

    def delete_user(self, username): return self._make_request("DELETE", f"/user/{username}")

    def login(self, username, password): return self._make_request("GET", "/user/login",
                                                                   params={"username": username, "password": password})

    def logout(self): return self._make_request("GET", "/user/logout")

    def log_response(self, response: requests.Response, test_name: str = ""):
        """Логирование ответа для отладки"""
        print(f"\n{'=' * 50}")
        print(f"ТЕСТ: {test_name}")
        print(f"URL: {response.request.url}")
        print(f"СТАТУС: {response.status_code}")
        print(f"{'=' * 50}\n")