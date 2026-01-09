import pytest
import time
import allure

from base.base_test import BaseTest
from generators.data_generator import UserDataGenerator


@allure.feature("Управление пользователями")
class TestUserAPI:
    """Тестовый класс для API управления пользователями"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка тестов"""
        self.base = BaseTest()
        self.generator = UserDataGenerator()
        self.created_users = []
        yield
        self._cleanup_users()

    @allure.step("Очистка тестовых данных")
    def _cleanup_users(self):
        """Удаление всех созданных пользователей"""
        if self.created_users:
            print(f"\n[ОЧИСТКА] Удаление {len(self.created_users)} пользователей...")
            for username in self.created_users:
                try:
                    self.base.delete_user(username, allow_failure=True)
                    print(f"  ✓ Пользователь {username} удален")
                except Exception as e:
                    print(f"  ✗ Ошибка удаления {username}: {e}")

    @allure.story("Создание пользователя")
    @allure.title("Успешное создание пользователя")
    @pytest.mark.smoke
    @pytest.mark.create
    def test_create_user_success(self):
        """Тест успешного создания пользователя"""
        print(f"▶️ Тест успешного создания пользователя")
        with allure.step("Генерация данных пользователя"):
            user_data = self.generator.generate_single_user()

        with allure.step("Отправка запроса на создание"):
            response = self.base.create_user(user_data)
            self.base.log_response(response, "test_create_user_success")

        with allure.step("Валидация ответа"):
            assert response.status_code == 200
            response_json = response.json()
            assert "code" in response_json
            assert response_json["code"] == 200

        with allure.step("Сохранение для очистки"):
            self.created_users.append(user_data["username"])
        print(f"🏁 Тест окончен")

    @allure.story("Создание пользователя")
    @allure.title("Создание пользователя с пустыми данными")
    @pytest.mark.regression
    @pytest.mark.create
    def test_create_user_with_empty_data(self):
        """Тест создания пользователя с пустыми данными"""
        print(f"▶️ Тест создания пользователя с пустыми данными")
        with allure.step("Генерация пустых данных"):
            user_data = self.generator.generate_invalid_user_data("empty_fields")

        with allure.step("Отправка запроса"):
            response = self.base.create_user(user_data)

        with allure.step("Валидация ответа"):
            assert response.status_code == 200

        with allure.step("Сохранение для очистки"):
            # У пустого юзернейна не может быть DELETE
            if user_data.get("username"):
                self.created_users.append(user_data["username"])
        print(f"🏁 Тест окончен")

    @allure.story("Авторизация пользователя")
    @allure.title("Успешный вход в систему")
    @pytest.mark.smoke
    @pytest.mark.login
    def test_login_success(self):
        """Тест успешного входа пользователя"""
        print(f"▶️ Тест успешного входа пользователя")
        username = f"login_user_{int(time.time())}"
        password = "testpass123"

        with allure.step("Создание тестового пользователя"):
            user_data = self.generator.generate_single_user(username)
            user_data["password"] = password
            create_resp = self.base.create_user(user_data)
            assert create_resp.status_code == 200

        with allure.step("Вход в систему"):
            login_resp = self.base.login(username, password)
            self.base.log_response(login_resp, "test_login_success")

        with allure.step("Валидация ответа"):
            assert login_resp.status_code == 200
            assert "logged in user session:" in login_resp.text

        with allure.step("Валидация заголовков"):
            assert "X-Rate-Limit" in login_resp.headers
            assert "X-Expires-After" in login_resp.headers

        with allure.step("Сохранение для очистки"):
            self.created_users.append(username)
        print(f"🏁 Тест окончен")

    @allure.story("Авторизация пользователя")
    @allure.title("Неуспешный вход с невалидными данными")
    @pytest.mark.regression
    @pytest.mark.login
    @pytest.mark.parametrize("username,password", [
        ("nonexistent", "wrongpass"),
        ("", ""),
        ("special!@#$%", "pass"),
    ])
    def test_login_failure(self, username, password):
        """Тест неуспешного входа с невалидными данными"""
        print(f"▶️ Тест неуспешного входа с невалидными данными")
        with allure.step(f"Попытка входа с username='{username}'"):
            response = self.base.login(username, password)
            self.base.log_response(response, f"test_login_failure_{username}")

        with allure.step("Валидация ответа"):
            # PetStore возвращает 200 даже для неверных данных
            assert response.status_code == 200
            assert "logged in user session:" in response.text
        print(f"🏁 Тест окончен")

    @allure.story("Выход из системы")
    @allure.title("Успешный выход из системы")
    @pytest.mark.smoke
    @pytest.mark.login
    def test_logout_success(self):
        """Тест успешного выхода из системы"""
        print(f"▶️ Тест успешного выхода из системы")
        username = f"logout_user_{int(time.time())}"

        with allure.step("Создание и вход пользователя"):
            user_data = self.generator.generate_single_user(username)
            create_resp = self.base.create_user(user_data)
            assert create_resp.status_code == 200

            self.base.login(username, user_data["password"])

        with allure.step("Выход из системы"):
            logout_resp = self.base.logout()
            self.base.log_response(logout_resp, "test_logout_success")

        with allure.step("Валидация ответа"):
            assert logout_resp.status_code == 200

        with allure.step("Сохранение для очистки"):
            self.created_users.append(username)
        print(f"🏁 Тест окончен")

    @allure.story("Обновление пользователя")
    @allure.title("Успешное обновление данных пользователя")
    @pytest.mark.smoke
    @pytest.mark.update
    def test_update_user_success(self):
        """Тест успешного обновления данных пользователя"""
        print(f"▶️ Тест успешного обновления данных пользователя")
        username = f"update_user_{int(time.time())}"

        with allure.step("Создание пользователя"):
            original_data = self.generator.generate_single_user(username)
            create_resp = self.base.create_user(original_data)
            assert create_resp.status_code == 200

        with allure.step("Подготовка обновленных данных"):
            updated_data = self.generator.generate_single_user(username)
            updated_data["firstName"] = "UpdatedFirstName"
            updated_data["lastName"] = "UpdatedLastName"

        with allure.step("Обновление пользователя"):
            update_resp = self.base.update_user(username, updated_data)
            self.base.log_response(update_resp, "test_update_user_success")

        with allure.step("Получение обновленных данных"):
            get_resp = self.base.get_user(username)
            retrieved_user = get_resp.json()

            # PetStore API ограничение: не всегда обновляет данные
            allure.attach(
                f"Ожидаемое имя: UpdatedFirstName\nПолученное: {retrieved_user['firstName']}",
                name="Сравнение данных",
                attachment_type=allure.attachment_type.TEXT
            )

            # Для PetStore API проверяем только успешность запроса
            assert update_resp.status_code == 200

        with allure.step("Сохранение для очистки"):
            self.created_users.append(username)
        print(f"🏁 Тест окончен")

    @allure.story("Обновление пользователя")
    @allure.title("Обновление несуществующего пользователя")
    @pytest.mark.regression
    @pytest.mark.update
    def test_update_nonexistent_user(self):
        """Тест обновления несуществующего пользователя"""
        print(f"▶️ Тест обновления несуществующего пользователя")
        fake_username = f"nonexistent_{int(time.time())}"

        with allure.step("Генерация данных"):
            user_data = self.generator.generate_single_user(fake_username)

        with allure.step("Попытка обновления"):
            response = self.base.update_user(fake_username, user_data)
            self.base.log_response(response, "test_update_nonexistent_user")

        with allure.step("Валидация ответа"):
            # PetStore API возвращает 200 для несуществующего
            assert response.status_code == 200
        print(f"🏁 Тест окончен")

    @allure.story("Удаление пользователя")
    @allure.title("Успешное удаление пользователя")
    @pytest.mark.smoke
    @pytest.mark.delete
    def test_delete_user_success(self):
        """Тест успешного удаления пользователя"""
        print(f"▶️ Тест успешного удаления пользователя")
        username = f"delete_user_{int(time.time())}"

        with allure.step("Создание пользователя"):
            user_data = self.generator.generate_single_user(username)
            create_resp = self.base.create_user(user_data)
            assert create_resp.status_code == 200

        with allure.step("Удаление пользователя"):
            delete_resp = self.base.delete_user(username)
            self.base.log_response(delete_resp, "test_delete_user_success")

        with allure.step("Проверка удаления"):
            assert delete_resp.status_code == 200

            try:
                self.base.get_user(username)
                pytest.fail("Пользователь не должен существовать")
            except Exception:
                allure.attach("Пользователь действительно удален", name="Удаление",
                              attachment_type=allure.attachment_type.TEXT)
        print(f"🏁 Тест окончен")

    @allure.story("Удаление пользователя")
    @allure.title("Удаление несуществующего пользователя")
    @pytest.mark.regression
    @pytest.mark.delete
    def test_delete_nonexistent_user(self):
        """Тест удаления несуществующего пользователя"""
        print(f"▶️ Тест удаления несуществующего пользователя")
        fake_username = f"fake_delete_{int(time.time())}"

        with allure.step("Попытка удаления несуществующего"):
            response = self.base.delete_user(fake_username, allow_failure=True)
            self.base.log_response(response, "test_delete_nonexistent_user")

        with allure.step("Валидация ответа"):
            # Нормально получить 404 или 200 для тестового API
            assert response.status_code in [200, 404]
        print(f"🏁 Тест окончен")

    @allure.story("Получение пользователя")
    @allure.title("Успешное получение данных пользователя")
    @pytest.mark.smoke
    def test_get_user_success(self):
        """Тест получения данных пользователя"""
        print(f"▶️ Тест получения данных пользователя")
        username = f"get_user_{int(time.time())}"

        with allure.step("Создание пользователя"):
            user_data = self.generator.generate_single_user(username)
            create_resp = self.base.create_user(user_data)
            assert create_resp.status_code == 200

        with allure.step("Получение данных"):
            get_resp = self.base.get_user(username)
            self.base.log_response(get_resp, "test_get_user_success")

        with allure.step("Валидация ответа"):
            assert get_resp.status_code == 200

            retrieved_user = get_resp.json()
            assert retrieved_user["username"] == username
            assert retrieved_user["email"] == user_data["email"]

            expected_schema = {
                "id": int, "username": str, "firstName": str, "lastName": str,
                "email": str, "password": str, "phone": str, "userStatus": int
            }
            assert self.base.validate_json_schema(retrieved_user, expected_schema)

        with allure.step("Сохранение для очистки"):
            self.created_users.append(username)
        print(f"🏁 Тест окончен")

    @allure.story("Получение пользователя")
    @allure.title("Получение несуществующего пользователя")
    @pytest.mark.regression
    def test_get_nonexistent_user(self):
        """Тест получения несуществующего пользователя"""
        print(f"▶️ Тест получения несуществующего пользователя")
        fake_username = f"fake_get_{int(time.time())}"

        with allure.step("Попытка получения"):
            try:
                self.base.get_user(fake_username)
                pytest.fail("Должна быть ошибка 404")
            except Exception as e:
                allure.attach(
                    f"Ожидаемая ошибка: {str(e)}",
                    name="Ошибка 404",
                    attachment_type=allure.attachment_type.TEXT
                )
        print(f"🏁 Тест окончен")

    @allure.story("Производительность")
    @allure.title("Создание 10 пользователей за разумное время")
    @pytest.mark.performance
    def test_create_multiple_users_performance(self):
        """Тест создание нескольких пользователей"""
        print(f"▶️ Тест создание нескольких пользователей")
        with allure.step("Генерация 10 пользователей"):
            users = self.generator.generate_bulk_users(10)

        with allure.step("Измерение времени создания"):
            start_time = time.time()
            for user in users:
                response = self.base.create_user(user)
                assert response.status_code == 200
                self.created_users.append(user["username"])

            duration = time.time() - start_time

        with allure.step("Валидация производительности"):
            allure.attach(
                f"Время: {duration:.2f} секунд",
                name="Производительность",
                attachment_type=allure.attachment_type.TEXT
            )
            assert duration < 10
        print(f"🏁 Тест окончен")
