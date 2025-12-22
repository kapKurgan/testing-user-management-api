# mock_petstore.py
# Полноценная имитация PetStore API для тестирования
# Реализует все необходимые эндпоинты: POST/GET/PUT/DELETE /user и /user/login/logout

from flask import Flask, request, jsonify
import time
import uuid

app = Flask(__name__)

# Хранилище пользователей в памяти (имитирует базу данных)
# Ключ: username, Значение: dict с данными пользователя
users_db = {}


# --- Эндпоинты управления пользователями ---

@app.route('/v2/user', methods=['POST'])
def create_user():
    """
    Создание нового пользователя
    Ожидает JSON с данными пользователя
    Возвращает: 200 + сообщение об успехе
    """
    user_data = request.get_json() or {}

    # Проверка наличия обязательного поля username
    if not user_data.get('username'):
        return jsonify({
            "code": 400,
            "type": "error",
            "message": "Username is required"
        }), 400

    username = user_data['username']

    # Проверка существования пользователя
    if username in users_db:
        return jsonify({
            "code": 400,
            "type": "error",
            "message": f"User '{username}' already exists"
        }), 400

    # Сохранение пользователя в "базу данных"
    users_db[username] = user_data

    # Успешный ответ (как в реальном PetStore API)
    return jsonify({
        "code": 200,
        "type": "unknown",
        "message": str(len(users_db))  # Возвращает количество пользователей
    }), 200


@app.route('/v2/user/<username>', methods=['GET'])
def get_user(username):
    """
    Получение данных пользователя по username
    Возвращает: 200 + данные пользователя или 404 если не найден
    """
    if username not in users_db:
        return jsonify({
            "code": 1,
            "type": "error",
            "message": "User not found"
        }), 404

    # Возвращаем данные пользователя
    return jsonify(users_db[username]), 200


@app.route('/v2/user/<username>', methods=['PUT'])
def update_user(username):
    """
    Обновление данных пользователя
    Возвращает: 200 + сообщение об успехе
    """
    user_data = request.get_json() or {}

    if username not in users_db:
        return jsonify({
            "code": 1,
            "type": "error",
            "message": "User not found"
        }), 404

    # Обновляем данные пользователя
    users_db[username].update(user_data)

    return jsonify({
        "code": 200,
        "type": "unknown",
        "message": str(len(users_db))
    }), 200


@app.route('/v2/user/<username>', methods=['DELETE'])
def delete_user(username):
    """
    Удаление пользователя
    Возвращает: 200 + сообщение об успехе или 404 если не найден
    """
    if username not in users_db:
        return jsonify({
            "code": 1,
            "type": "error",
            "message": "User not found"
        }), 404

    # Удаляем пользователя из базы
    del users_db[username]

    return jsonify({
        "code": 200,
        "type": "unknown",
        "message": username
    }), 200


# --- Эндпоинты авторизации ---

@app.route('/v2/user/login', methods=['GET'])
def login_user():
    """
    Вход пользователя в систему
    Ожидает query-параметры: username, password
    Возвращает: 200 + токен сессии
    """
    username = request.args.get('username')
    password = request.args.get('password')

    # Проверка наличия параметров
    if not username or not password:
        return jsonify({
            "code": 400,
            "type": "error",
            "message": "Username and password are required"
        }), 400

    # В реальном PetStore API проверка не строгая - всегда возвращает 200
    # Мы имитируем это поведение
    session_token = f"logged in user session:{uuid.uuid4()}"

    # Добавляем стандартные заголовки, которые ожидают тесты
    response = jsonify({
        "code": 200,
        "type": "unknown",
        "message": session_token
    })

    response.headers['X-Rate-Limit'] = '1000'
    response.headers['X-Expires-After'] = f'{int(time.time()) + 3600}'

    return response, 200


@app.route('/v2/user/logout', methods=['GET'])
def logout_user():
    """
    Выход пользователя из системы
    Возвращает: 200 + сообщение об успехе
    """
    return jsonify({
        "code": 200,
        "type": "unknown",
        "message": "ok"
    }), 200


# --- Вспомогательные эндпоинты ---

@app.route('/health', methods=['GET'])
def health_check():
    """
    Healthcheck для Docker Compose
    Возвращает простой 200 OK когда сервис готов
    """
    return jsonify({
        "status": "healthy",
        "users_count": len(users_db)
    }), 200


@app.route('/v2/user/login', methods=['HEAD'])
def login_head():
    """
    HEAD запрос для healthcheck (Docker Compose может использовать)
    """
    return '', 200


# --- Запуск приложения ---

if __name__ == '__main__':
    # Запуск Flask на порту 8080, доступен для всех интерфейсов (0.0.0.0)
    # Важно: debug=False для production, threaded=True для параллельных запросов
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)