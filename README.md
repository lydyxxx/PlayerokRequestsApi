# Playerok Requests API

**Playerok Requests API** — это неофициальный Python-клиент для [Playerok.com](https://playerok.com/). Он использует GraphQL-запросы для работы с некоторыми функциями платформы, в том числе получения информации о пользователях и взаимодействия с чатами.

> **Внимание**: Проект не имеет официальной поддержки или одобрения со стороны Playerok.com. Используйте его на свой страх и риск.

---

## Возможности

1. **Загрузка куки из локального JSON-файла** и использование их при всех запросах.  
2. **Получение данных о пользователе** (никнейм, количество отзывов, количество товаров и т.д.).  
3. **Получение идентификатора пользователя** по его никнейму.  
4. **Получение идентификатора чата** с конкретным пользователем.  
5. **Отправка текстового сообщения** в чат с выбранным пользователем.  

---

## Описание основных методов

### 1. `get_id(username) -> str | None`
Возвращает `user_id` для пользователя с указанным `username`, если такой пользователь существует. В случае ошибки или если пользователь не найден, возвращает `None` - этот метод исключительно использовать со своим username!.

### 2. `get_profile(username) -> tuple | None`
Возвращает кортеж из 7 значений с данными профиля, либо `None` в случае ошибки:

1. **nickname (str)** — Никнейм пользователя  
2. **testimonial_count (int)** — Количество отзывов  
3. **total_items (int)** — Общее количество товаров  
4. **purchases_total (int)** — Количество покупок (входящих сделок)  
5. **sales_total (int)** — Количество продаж (исходящих сделок)  
6. **active_items (int)** — Количество активных товаров (`total_items - finished_items`)  
7. **finished_items (int)** — Количество завершённых товаров  

### 3. `on_username_id_get(profileusername, username) -> str | None`
Ищет чат, в котором участвуют `profileusername` (профиль, от лица которого вы ведёте переписку) и `username` (тот, кому вы пишете). Если такой чат найден, метод возвращает его идентификатор (`chat_id`). Если чат не найден, возвращает `None`.

### 4. `on_send_message(profileusername, username, text) -> dict | None`
Отправляет сообщение `text` в чат между пользователями `profileusername` и `username`.  
- Перед отправкой автоматически пытается определить `chat_id` с помощью `on_username_id_get()`.  
- Если сообщение успешно отправлено, метод возвращает `dict` с полным GraphQL-ответом.  
- Если отправить сообщение не удалось (нет нужного `chat_id`, либо ответ от GraphQL не соответствует ожидаемому), метод вернёт `None`.  

Пример успешного ответа:
```json
{
  "data": {
    "createChatMessage": {
      "id": "1eff866b-5a11-6480-27cf-72b2c009cc5e",
      "text": "?",
      "createdAt": "2025-03-03T19:35:48.936Z",
      "user": {
        "id": "1ee2e4f3-6775-6b70-e5c9-bf2595cd157f",
        "username": "username"
      },
      ...
    }
  }
}
```


### ПРИМЕР
```python
from PlayerokApi import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="cookies.json")
myProfile = 'username'
# Получить свой ID пользователя
user_id = api.get_id("username")
print(user_id)

# Получить данные своего профиля
profile_data = api.get_profile("username")
print(profile_data)

# Найти идентификатор чата и отправить сообщение
chat_id = api.on_username_id_get(myProfile, "otherUser")
message_response = api.on_send_message(myProfile, "otherUser", "Hello!")
```
