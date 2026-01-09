# Тестирование API "Управление пользователями"

## Цель

Создание автоматизированного тестового фреймворка для проверки функциональности API управления пользователями на базе PetStore Swagger API с генерацией тестовых данных, системой отчетности.


## Задачи

- Разработка базового архитектурного каркаса с реиспользуемыми компонентами
- Реализация генерации валидных и невалидных тестовых данных
- Создание покрытия CRUD-операций пользователей (создание, чтение, обновление, удаление)
- Реализация сценариев аутентификации (вход/выход)
- Подключение системы отчетности (Allure, HTML)
- Обеспечение устойчивости тестов к ошибкам и автоматической очистки данных

---

## Оглавление

- [Структура проекта](#структура-проекта)
- [Основные компоненты](#основные-компоненты)
- [Поддерживаемые сценарии](#поддерживаемые-сценарии)
- [Тестовые сценарии](#тестовые-сценарии)
- [Локальный запуск тестов](#локальный-запуск-тестов)
- [Локальный просмотр Allure отчета](#локальный-просмотр-allure-отчета)
- [CI/CD](#cicd)
- [URL отчетов GitHub Pages](#url-отчетов-github-pages)
- [Требования](#требования)
- [Интеграция с GitHub Actions](#интеграция-с-github-actions)

---

## Структура проекта

```bash
framework-for-testing-functionality-user-management-API/
|-- pytest.ini                     # Конфигурация pytest
|-- conftest.py                    # Фикстуры и настройка окружения
|-- requirements.txt               # Зависимости Python
|-- base/
|   `-- base_test.py               # Базовый класс с HTTP-методами
|-- generators/
|   `-- data_generator.py          # Генератор тестовых данных
|-- reports/
|   
`-- tests/
    `-- test_user_api.py           # Тестовые сценарии
```

---

## Основные компоненты

[**BaseTest**](./base/base_test.py)

- Универсальный базовый класс для всех API-тестов
- Прямое обращение к реальному PetStore API (URL захардкожен)
- Поддержка Allure-отчетности (шаги, вложения, логирование)
- Автоматическая валидация HTTP-статусов
- Методы для всех операций: create_user, get_user, update_user, delete_user, login, logout
- Валидация JSON-схем

[**UserDataGenerator**](./generators/data_generator.py)

- Генерация реалистичных тестовых данных через Faker
- Поддержка различных локализаций
- Генерация валидных и невалидных данных
- Создание пакетных данных

[**TestUserAPI**](./tests/test_user_api.py)

- 14 тестовых сценариев покрывающих все граничные случаи
- 100% покрытие CRUD-операций
- Сегментация тестов по маркерам (smoke, regression, performance)
- Автоматическая очистка тестовых данных
- Параметризованные негативные тесты

---

## Поддерживаемые сценарии

- Валидные данные (username, email, password, etc.)
- Пустые поля (граничное значение)
- Невалидный email-формат
- Превышение максимальной длины полей
- Пользователи с конкретным статусом

---

## Тестовые сценарии

```bash
---------------------------------------------------------------------------------------------------------------
| ID  | Название                               | Маркер             | Описание                                |
|-----| ---------------------------------------|--------------------|-----------------------------------------|
| 1   | test_create_user_success               | smoke, create      | Создание валидного пользователя         |
| 2   | test_create_user_with_empty_data       | regression, create | Создание пользователя с пустыми полями  |
| 3   | test_login_success                     | smoke, login       | Успешная аутентификация пользователя    |
| 4-6 | test_login_failure                     | regression, login  | Негативные сценарии входа               |
| 7   | test_logout_success                    | smoke, login       | Выход из системы                        |
| 8   | test_update_user_success               | smoke, update      | Обновление данных                       |
| 9   | test_update_nonexistent_user           | regression, update | Обновление несуществующего пользователя |
| 10  | test_delete_user_success               | smoke, delete      | Удаление пользователя                   |
| 11  | test_delete_nonexistent_user           | regression, delete | Удаление несуществующего пользователя   |
| 12  | test_get_user_success                  | smoke              | Получение данных пользователя           |
| 13  | test_get_nonexistent_user              | regression         | Получение несуществующего пользователя  |
| 14  | test_create_multiple_users_performance | performance        | Производительность                      |
---------------------------------------------------------------------------------------------------------------
```

---

## Локальный запуск тестов

### Базовый запуск
```bash
pytest
```

### С подробным выводом
```bash
pytest -v -s
```

### Запуск по маркерам
```bash
pytest -m smoke          # Только критические тесты
pytest -m regression     # Только регрессионные тесты
pytest -m login          # Только тесты входа
```
Все маркеры указаны в разделе: [Тестовые сценарии](#тестовые-сценарии)

### С генерацией HTML отчета
```bash
pytest --html=reports/pytest_report.html
```

### С генерацией Allure отчета
```bash
pytest --alluredir=reports/allure-results
```

---
  
## Локальный просмотр Allure отчета
```bash
allure serve reports/allure-results
```

---

## CI/CD

В этом проекте включена интеграция с GitHub Actions. Вы можете выполнять сценарии в автономном режиме и автоматически публиковать отчеты на страницах GitHub.

Конфигурацию можно найти в [api-tests.yml](./.github/workflows/api-tests.yml).   

Автоматический запуск через интерфейс GitHub:
- [Перейдите в Actions > API Tests > Run workflow](https://github.com/kapKurgan/testing-user-management-api/actions)
- Выберите сценарий тестов (например, **-m login**)
- Нажмите **workflow**
- Система выполнит тесты напрямую к https://petstore.swagger.io

---

## URL отчетов GitHub Pages

### HTML
```bash
https://kapKurgan.github.io/testing-user-management-api/<run_id>/pytest-report.html
```

Например:
https://kapKurgan.github.io/testing-user-management-api/20845595725/pytest-report.html


### ALLURE 
```bash
https://kapKurgan.github.io/testing-user-management-api/<run_id>/allure-report/index.html
```

Например:
https://kapKurgan.github.io/testing-user-management-api/20845595725/allure-report/index.html

---

## Требования
- Python 3.12+
- GitHub account (для CI/CD и GitHub Pages)

Установка зависимостей:
```bash
pip install -r requirements.txt
```

--- 

## Интеграция с GitHub Actions

Workflow автоматически:
- Устанавливает Python 3.12
- Устанавливает зависимости
- Запускает тесты к реальному API
- Генерирует HTML-отчеты
- Публикует отчеты в GitHub Pages

---
