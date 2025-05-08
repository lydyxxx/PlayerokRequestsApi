# Документация API Пользователи

Модуль `PlayerokUsersApi` предоставляет функционал для управления информацией о пользователях на платформе Playerok. Он позволяет получать данные о профиле, балансе, а также ID пользователя по его имени.

## Инициализация

```python
from PlayerokRequestsApi.users import PlayerokUsersApi

api = PlayerokUsersApi(cookies_file="cookies.json", logger=False)
```

- **cookies_file**: Путь к файлу с cookies для аутентификации (по умолчанию `cookies.json`).
- **logger**: Включение/выключение логирования (по умолчанию `False`).

## Методы

| Метод                     | Описание                                                                 | Возвращаемое значение                     |
|---------------------------|--------------------------------------------------------------------------|------------------------------------------|
| `get_username()`          | Получает имя пользователя и ID текущего аккаунта из cookies.             | Кортеж `(username, id)` или `('', '')` при ошибке. |
| `get_id_for_username(username)` | Получает ID пользователя по его имени.                              | `str` (ID) или `None` при ошибке.        |
| `get_balance()`           | Получает информацию о балансе аккаунта.                                  | Словарь с ключами `AllBalance`, `available`, `pendingIncome`, `frozen` или `None`. |
| `get_full_info()`         | Получает полную информацию о профиле пользователя.                       | Словарь с данными профиля или `None`.    |
| `get_profile()`           | Получает краткую информацию о профиле (ник, отзывы, товары, сделки).     | Кортеж `(nickname, testimonial_count, total_items, purchases_total, sales_total, active_items, finished_items)` или `None`. |

## Пример использования

### Получение профиля пользователя

```python
profile = api.get_profile()
if profile:
    print(f"Ник: {profile[0]}")
    print(f"Количество отзывов: {profile[1]}")
    print(f"Всего товаров: {profile[2]}")
else:
    print("Ошибка при получении профиля")
```

### Получение баланса

```python
balance = api.get_balance()
if balance:
    print(f"Общий баланс: {balance['AllBalance']}")
    print(f"Доступно: {balance['available']}")
else:
    print("Ошибка при получении баланса")
```

## Обработка ошибок

- При ошибках запросов (например, неверные cookies или проблемы с API) методы возвращают `None` и выводят сообщение об ошибке.
- Включите логирование (`logger=True`) для получения дополнительной информации об ошибках.