import pytest
from base.base_test import BaseTest
from generators.data_generator import UserDataGenerator


class TestUserAPI:
    """Тестовый класс для API управления пользователями"""

    def setup(self):
        """Настройка тестов"""
        self.base = BaseTest()
        self.generator = UserDataGenerator()

    def test_create_user_success(self):
        """Тест успешного создания пользователя"""
        user_data = self.generator.generate_single_user()
        response = self.base.create_user(user_data)
        assert response.status_code == 200