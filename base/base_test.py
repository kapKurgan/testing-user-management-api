import requests
from typing import Dict, Any, Optional
import json
import allure
import os


class BaseTest:
    """Базовый класс для всех тестов API"""

    BASE_URL = os.getenv("API_BASE_URL", "https://petstore.swagger.io/v2")
    TIMEOUT = 10

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    @allure.step("Выполнение {method} запроса к {endpoint}")
    def _make_request(
            self,
            method: str,
            endpoint: str,
            data: Optional[Dict] = None,
            params: Optional[Dict] = None,
            expected_status: int = 200,
            allow_failure: bool = False
    ) -> requests.Response:
        """Универсальный метод для выполнения HTTP-запросов"""
        url = f"{self.BASE_URL}{endpoint}"

        allure.attach(
            f"URL: {url}\nMethod: {method}\nData: {json.dumps(data, indent=2) if data else 'None'}\nParams: "
            f"{json.dumps(params, indent=2) if params else 'None'}",
            name="Запрос",
            attachment_type=allure.attachment_type.JSON
        )

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                json=data,
                params=params,
                timeout=self.TIMEOUT
            )

            if not allow_failure:
                response.raise_for_status()

            allure.attach(
                f"Status: {response.status_code}\nBody: {response.text}",
                name="Ответ",
                attachment_type=allure.attachment_type.JSON
            )

            if response.status_code != expected_status:
                print(f"[!] Ожидаемый статус: {expected_status}, Получен: {response.status_code}")
                allure.attach(
                    f"Ожидаемый статус: {expected_status}, Получен: {response.status_code}",
                    name="Ошибка статуса",
                    attachment_type=allure.attachment_type.TEXT
                )

            return response

        except requests.exceptions.RequestException as e:
            error_msg = f"[ERROR] Ошибка запроса: {method} {url}\nДетали: {str(e)}"
            print(error_msg)
            allure.attach(
                error_msg,
                name="Ошибка запроса",
                attachment_type=allure.attachment_type.TEXT
            )
            if not allow_failure:
                raise
            else:
                # Создаем dummy response для тестов с ожидаемыми ошибками
                dummy_response = requests.Response()
                dummy_response.status_code = 404
                dummy_response._content = b'{"error": "Not Found"}'
                return dummy_response

    @allure.step("Создание пользователя")
    def create_user(self, user_data: Dict[str, Any]) -> requests.Response:
        """Создание пользователя"""
        return self._make_request("POST", "/user", data=user_data, expected_status=200)

    @allure.step("Получение пользователя {username}")
    def get_user(self, username: str) -> requests.Response:
        """Получение данных пользователя"""
        return self._make_request("GET", f"/user/{username}", expected_status=200)

    @allure.step("Обновление пользователя {username}")
    def update_user(self, username: str, user_data: Dict[str, Any]) -> requests.Response:
        """Обновление данных пользователя"""
        return self._make_request("PUT", f"/user/{username}", data=user_data, expected_status=200)

    @allure.step("Удаление пользователя {username}")
    def delete_user(self, username: str, allow_failure: bool = False) -> requests.Response:
        """Удаление пользователя"""
        return self._make_request("DELETE", f"/user/{username}", expected_status=200, allow_failure=allow_failure)

    @allure.step("Авторизация пользователя {username}")
    def login(self, username: str, password: str) -> requests.Response:
        """Авторизация пользователя"""
        return self._make_request(
            "GET",
            "/user/login",
            params={"username": username, "password": password},
            expected_status=200
        )

    @allure.step("Выход из системы")
    def logout(self) -> requests.Response:
        """Выход из системы"""
        return self._make_request("GET", "/user/logout", expected_status=200)

    @allure.step("Логирование ответа")
    def log_response(self, response: requests.Response, test_name: str = ""):
        """Логирование ответа для отладки"""
        log_data = f"""
            {'=' * 50}
            ТЕСТ: {test_name}
            URL: {response.request.url}
            МЕТОД: {response.request.method}
            СТАТУС: {response.status_code}
            ТЕЛО ЗАПРОСА: {response.request.body[:200] if response.request.body else 'None'}
            ОТВЕТ: {response.text[:200]}
            {'=' * 50}
            """
        print(log_data)
        allure.attach(log_data, name=f"Лог: {test_name}", attachment_type=allure.attachment_type.TEXT)

    @allure.step("Валидация JSON схемы")
    def validate_json_schema(self, response_data: Dict, expected_schema: Dict) -> bool:
        """Базовая валидация JSON схемы"""
        try:
            for key, value_type in expected_schema.items():
                if key not in response_data:
                    allure.attach(f"Отсутствует ключ: {key}", name="Ошибка схемы",
                                  attachment_type=allure.attachment_type.TEXT)
                    return False

                if not isinstance(response_data[key], value_type):
                    allure.attach(
                        f"Неверный тип для {key}: ожидается {value_type}, получен {type(response_data[key])}",
                        name="Ошибка типа",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    return False

            return True

        except Exception as e:
            allure.attach(f"Ошибка валидации: {e}", name="Исключение", attachment_type=allure.attachment_type.TEXT)
            return False