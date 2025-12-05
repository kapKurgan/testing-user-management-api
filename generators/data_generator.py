from faker import Faker
import random
from typing import Dict, Any, List

class UserDataGenerator:
    """Генератор тестовых данных для пользователей"""

    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)
        self.user_statuses = [0, 1, 2, 3]

    def generate_single_user(self, username: str = None) -> Dict[str, Any]:
        """Генерация данных одного пользователя"""
        return {
            "id": random.randint(1000, 99999),
            "username": username or self.fake.user_name(),
            "firstName": self.fake.first_name(),
            "lastName": self.fake.last_name(),
            "email": self.fake.email(),
            "password": self.fake.password(),
            "phone": self.fake.phone_number(),
            "userStatus": random.choice(self.user_statuses)
        }

    def generate_bulk_users(self, count: int = 5) -> List[Dict[str, Any]]:
        """Генерация списка пользователей"""
        return [self.generate_single_user() for _ in range(count)]

