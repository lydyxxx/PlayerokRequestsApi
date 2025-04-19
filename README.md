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

### 5. `get_balance(myProfile) -> str | None`
Возвращает кортеж из 3 значений с данными баланса вашего профиля:
{'AllBalance': 0.00, 'available': 0.00, 'pendingIncome': 0.00, 'frozen': 0.00}
1. **AllBalance** - Общий баланс (Учитывая средства замороженные так-же которые идут и доступные)
2. **available** - Баланс доступный к выводу
3. **pendingIncome** - Баланс который уже подтверждён
4. **frozen** - Замороженый баланс (возможный баланс который если получение товара подтвердит покупатель)
   
### 6. `get_full_info(myProfile) -> str | None`
Возвращает полный кортеж всей информации о профиле.

### ПРИМЕРЫ ЗАПРОСОВ И ИХ ОТВЕТЫ
### Запрос get_id
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="cookies.json")
myProfile = 'username'

idProfile = api.get_id(myProfile)
print(idProfile)
```

### Ответ

```string
id-profile
```

### Запрос get_profile
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="cookies.json")
myProfile = 'username'

profile = api.get_profile(myProfile)
print(profile)
```

### Ответ

```json
(
'username',
testimonial_count,
total_items,
purchases_total,
sales_total,
active_items,
finished_items
)
```


### Запрос on_username_id_get
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="cookies.json")
myProfile = 'username'
profileInterlocutor = 'username2'

chatId = api.on_username_id_get(myProfile, profileInterlocutor)
print(chatId)
```

### Ответ

```json
chat-id
```


### Запрос on_send_message
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="cookies.json")
myProfile = 'username'
profileInterlocutor = 'username2'
textMessage = 'Hello!'

ProcessSendMessage = api.on_send_message(myProfile, profileInterlocutor, textMessage)
```

### Запрос get_balance
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="cookies.json")
myProfile = 'username'

balance = api.get_balance(myProfile)
print(balance)
```

### Ответ

```json
{
'AllBalance': float,
'available': float,
'pendingIncome': float,
'frozen': float
}
```

### Запрос get_full_info
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="cookies.json")
myProfile = 'username'

info = api.get_full_info(myProfile)
print(info)
```

### Ответ

```json
{
'id': 'id',
'isBlocked': False,
'isVerified': None,
'isBlockedFor': None,
'hasFrozenBalance': False,
'username': 'username',
'email': 'username@mail.ru',
'role': 'USER',
'balance':
   {
      'id': 'id',
      'value': 0.00,
      'frozen': 0.00,
      'available': 0.00,
      'withdrawable': 0.00,
      'pendingIncome': 0.00,
      '__typename': 'UserBalance'
},
'profile':
   {
      'id': 'id',
      'username': 'username',
      'role': 'USER',
      'avatarURL': 'https://playerok.fra1.digitaloceanspaces.com/images/username.png',
      'isOnline': False, 'isBlocked': False,
      'rating': 0,
      'testimonialCounter': 0,
      'createdAt': '2023-06-03T12:32:50.461Z',
      'supportChatId': 'supportChatId',
      'systemChatId': 'systemChatId',
      '__typename': 'UserFragment'},
      'stats': {'id': 'id',
      'items': {'total': 0, 'finished': 0, '__typename': 'UserItemsStats'},
      'deals': {'incoming': {'total': 0, 'finished': 0, '__typename': 'IncomingUserDealsStats'},
      'outgoing': {'total': 0, 'finished': 0, '__typename': 'OutgoingUserDealsStats'}, '__typename': 'UserDealsStats'}, '__typename': 'UserStats'}, 'hasEnabledNotifications': True, 'supportChatId': 'supportChatId', 'systemChatId': 'SystemChatId', '__typename': 'User'}
```
