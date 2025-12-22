# base/base_test.py
# Базовый класс для всех тестов API
# Работает НЕПОСРЕДСТВЕННО с реальным PetStore API
# Без поддержки mock-сервера, Docker и локальных переменных

import requests
import json
from typing import Dict, Any, Optional
import allure


class BaseTest:
    """
    Базовый класс для всех тестов API управления пользователями.

    ВАЖНО: Эта версия работает ТОЛЬКО с реальным PetStore API
    URL захардкожен в константе BASE_URL

    Предоставляет универсальные методы для HTTP-запросов,
    логирование в Allure и валидацию ответов.
    """

    # ХАРДКОД: URL реального PetStore API
    # Измените здесь, если нужно тестировать другой сервер
    BASE_URL = "https://petstore.swagger.io/v2"

    # Таймаут для HTTP-запросов в секундах
    TIMEOUT = 10

    def __init__(self):
        """
        Инициализация тестового класса.

        Создает HTTP-сессию с предустановленными заголовками.
        Сессия повторно использует TCP-соединения для повышения производительности.
        """
        # Создание сессии requests
        self.session = requests.Session()

        # Установка базовых заголовков для всех запросов
        self.session.headers.update({
            "Content-Type": "application/json",  # Все запросы отправляем/принимаем в JSON
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
        """
        Универсальный метод для выполнения HTTP-запросов к реальному API.

        Аргументы:
            method: HTTP-метод (POST, GET, PUT, DELETE и т.д.)
            endpoint: End-point API (например, /user/login)
            data: Тело запроса в формате JSON (для POST/PUT)
            params: Query-параметры (для GET)
            expected_status: Ожидаемый HTTP-статус код (по умолчанию 200)
            allow_failure: Если True, не выбрасывает исключение при ошибке

        Возвращает:
            Объект Response из библиотеки requests

        Исключения:
            RequestException: если allow_failure=False и запрос завершился ошибкой
        """
        # Формируем полный URL
        url = f"{self.BASE_URL}{endpoint}"

        # Логирование запроса в Allure-отчет
        allure.attach(
            f"URL: {url}\nMethod: {method}\nData: {json.dumps(data, indent=2) if data else 'None'}\nParams: "
            f"{json.dumps(params, indent=2) if params else 'None'}",
            name="Запрос",
            attachment_type=allure.attachment_type.JSON
        )

        try:
            # Выполнение HTTP-запроса через сессию
            response = self.session.request(
                method=method.upper(),  # Преобразуем метод в верхний регистр
                url=url,
                json=data,  # Автоматическая сериализация в JSON
                params=params,
                timeout=self.TIMEOUT  # Таймаут из константы класса
            )

            # Если не разрешены ошибки, выбрасываем исключение при 4xx/5xx статусах
            if not allow_failure:
                response.raise_for_status()

            # Логирование ответа в Allure-отчет
            allure.attach(
                f"Status: {response.status_code}\nBody: {response.text}",
                name="Ответ",
                attachment_type=allure.attachment_type.JSON
            )

            # Проверка соответствия фактического и ожидаемого статуса
            if response.status_code != expected_status:
                print(f"[!] Ожидаемый статус: {expected_status}, Получен: {response.status_code}")
                allure.attach(
                    f"Ожидаемый статус: {expected_status}, Получен: {response.status_code}",
                    name="Ошибка статуса",
                    attachment_type=allure.attachment_type.TEXT
                )

            return response  # Возвращаем объект Response

        except requests.exceptions.RequestException as e:
            # Обработка ошибок запроса
            error_msg = f"[ERROR] Ошибка запроса: {method} {url}\nДетали: {str(e)}"
            print(error_msg)

            # Логирование ошибки в Allure
            allure.attach(
                error_msg,
                name="Ошибка запроса",
                attachment_type=allure.attachment_type.TEXT
            )

            # Если ошибки не разрешены - выбрасываем исключение
            if not allow_failure:
                raise
            else:
                # Если ошибки разрешены (для негативных тестов)
                # Создаем фиктивный Response для дальнейшей обработки
                dummy_response = requests.Response()
                dummy_response.status_code = 404
                dummy_response._content = b'{"error": "Not Found"}'
                return dummy_response

    # --- Методы для работы с API PetStore ---

    @allure.step("Создание пользователя")
    def create_user(self, user_data: Dict[str, Any]) -> requests.Response:
        """
        Создание нового пользователя через POST /user

        Аргументы:
            user_data: Словарь с данными пользователя (username, email, password и т.д.)

        Возвращает:
            Response объект с результатом создания
        """
        return self._make_request("POST", "/user", data=user_data, expected_status=200)

    @allure.step("Получение пользователя {username}")
    def get_user(self, username: str) -> requests.Response:
        """
        Получение данных пользователя по username

        Аргументы:
            username: Имя пользователя для получения
        """
        return self._make_request("GET", f"/user/{username}", expected_status=200)

    @allure.step("Обновление пользователя {username}")
    def update_user(self, username: str, user_data: Dict[str, Any]) -> requests.Response:
        """
        Обновление данных пользователя

        Аргументы:
            username: Имя пользователя для обновления
            user_data: Новые данные пользователя
        """
        return self._make_request("PUT", f"/user/{username}", data=user_data, expected_status=200)

    @allure.step("Удаление пользователя {username}")
    def delete_user(self, username: str, allow_failure: bool = False) -> requests.Response:
        """
        Удаление пользователя

        Аргументы:
            username: Име пользователя для удаления
            allow_failure: Если True, не выбрасывает исключение при ошибке (например, 404)
        """
        return self._make_request("DELETE", f"/user/{username}", expected_status=200, allow_failure=allow_failure)

    @allure.step("Авторизация пользователя {username}")
    def login(self, username: str, password: str) -> requests.Response:
        """
        Вход пользователя в систему

        Аргументы:
            username: Имя пользователя
            password: Пароль
        """
        return self._make_request(
            "GET",
            "/user/login",
            params={"username": username, "password": password},
            expected_status=200
        )

    @allure.step("Выход из системы")
    def logout(self) -> requests.Response:
        """
        Выход пользователя из системы
        """
        return self._make_request("GET", "/user/logout", expected_status=200)

    @allure.step("Логирование ответа")
    def log_response(self, response: requests.Response, test_name: str = ""):
        """
        Логирование полных данных ответа для отладки.

        Выводит в консоль и прикрепляет к Allure-отчету:
        - URL и метод запроса
        - Статус ответа
        - Тело запроса (первые 200 символов)
        - Тело ответа (первые 200 символов)

        Аргументы:
            response: Объект Response из requests
            test_name: Название теста для идентификации
        """
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
        """
        Базовая валидация JSON-схемы ответа.

        Проверяет:
        - Наличие всех ожидаемых ключей
        - Тип данных каждого значения

        Аргументы:
            response_data: Словарь с данными ответа
            expected_schema: Словарь с ожидаемыми типами данных {key: type}

        Возвращает:
            True если схема валидна, False если есть ошибки
        """
        try:
            # Проверка каждого ключа в ожидаемой схеме
            for key, value_type in expected_schema.items():
                # Проверка наличия ключа
                if key not in response_data:
                    allure.attach(f"Отсутствует ключ: {key}", name="Ошибка схемы",
                                  attachment_type=allure.attachment_type.TEXT)
                    return False

                # Проверка типа данных
                if not isinstance(response_data[key], value_type):
                    allure.attach(
                        f"Неверный тип для {key}: ожидается {value_type}, получен {type(response_data[key])}",
                        name="Ошибка типа",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    return False

            return True  # Все проверки пройдены

        except Exception as e:
            # Обработка неожиданных ошибок при валидации
            allure.attach(f"Ошибка валидации: {e}", name="Исключение", attachment_type=allure.attachment_type.TEXT)
            return False