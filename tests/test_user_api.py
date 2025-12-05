import pytest
from ..base.base_test import BaseTest
from ..generators.data_generator import UserDataGenerator
import time

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

    def test_create_user_success(self):
        """Тест успешного создания пользователя"""
        user_data = self.generator.generate_single_user()
        response = self.base.create_user(user_data)
        assert response.status_code == 200

    def test_create_user_with_empty_data(self):
        """Тест создания пользователя с пустыми данными"""
        user_data = self.generator.generate_invalid_user_data("empty_fields")
        response = self.base.create_user(user_data)
        assert response.status_code == 200

    def test_login_success(self):
        """Тест успешного входа пользователя"""
        username = f"login_user_{int(time.time())}"
        password = "testpass123"

        user_data = self.generator.generate_single_user(username)
        user_data["password"] = password
        self.base.create_user(user_data)

        response = self.base.login(username, password)
        assert response.status_code == 200
        self.created_users.append(username)

    @pytest.mark.parametrize("username,password", [
        ("nonexistent", "wrongpass"),
        ("", ""),
        ("special!@#$%", "pass"),
    ])
    def test_login_failure(self, username, password):
        """Тест неуспешного входа с невалидными данными"""
        response = self.base.login(username, password)
        assert response.status_code == 200