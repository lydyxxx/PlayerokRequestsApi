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
6. **Получение баланса пользователя** только пользователя чей cookie
7. **Получение полной информации о пользователе** только пользователя чей cookie
8. **Получение полной информации о товаре** если товар cookie значит в информации так-же будут скрытые данные, если товар не cookie то название,описание и т.п данные.
9. **Копирование товара** получение названия товара, описания, стоимости, картинки товара.  

---

## Зависимости

```pip install wrapper-tls-requests```

---


## Описание основных методов



### 1. `get_profile() -> tuple | None`
Возвращает кортеж из 7 значений с данными профиля, либо `None` в случае ошибки:

1. **nickname (str)** — Никнейм пользователя  
2. **testimonial_count (int)** — Количество отзывов  
3. **total_items (int)** — Общее количество товаров  
4. **purchases_total (int)** — Количество покупок (входящих сделок)  
5. **sales_total (int)** — Количество продаж (исходящих сделок)  
6. **active_items (int)** — Количество активных товаров (`total_items - finished_items`)  
7. **finished_items (int)** — Количество завершённых товаров  

### 2. `on_username_id_get() -> str | None`
Ищет чат, в котором участвуют `profileusername` (профиль, от лица которого вы ведёте переписку - больше не требуется!(автоматически указывает)) и `username` (тот, кому вы пишете). Если такой чат найден, метод возвращает его идентификатор (`chat_id`). Если чат не найден, возвращает `None`.

### 3. `on_send_message(profileusername, text) -> str | None`
Отправляет сообщение `text` в чат между пользователями `profileusername` и `username`.  
- Перед отправкой автоматически пытается определить `chat_id` с помощью `on_username_id_get()`.  
- Если сообщение успешно отправлено, метод возвращает `dict` с полным GraphQL-ответом.  
- Если отправить сообщение не удалось (нет нужного `chat_id`, либо ответ от GraphQL не соответствует ожидаемому), метод вернёт `None`.  

### 4. `get_balance() -> dict | None`
Возвращает кортеж из 3 значений с данными баланса вашего профиля:
{
'AllBalance': 0.00, 
'available': 0.00, 
'pendingIncome': 0.00, 
'frozen': 0.00
}
1. **AllBalance** - Общий баланс (Учитывая средства замороженные так-же которые идут и доступные)
2. **available** - Баланс доступный к выводу
3. **pendingIncome** - Баланс который уже подтверждён
4. **frozen** - Замороженый баланс (возможный баланс который если получение товара подтвердит покупатель)
   
### 5. `get_full_info() -> tuple | None`
Возвращает полный кортеж всей информации о профиле.

### 6. `get_product_data(link) -> tuple | None`
Возвращает полный кортеж всей информации о товаре.

### 7. `copy_product(link) -> dict | None`
Возвращает:
```json
{
'title': title, - Название товара
'description': description, - Описание товара
'rawprice': rawprice, - Изначальную цену выставленную при выставлении товара
'price': price, - Цена со скидкой
'attachments': - атачменты
   {
      'id': id,
      'url': url, - обложка товара
      '__typename': __typename
   }
}
```

### 8. `get_username() -> tuple | None`
Возвращает:
```json
{
'username': username,
'id': id
}
```

### 9. `get_lots() -> dict | None`
Возвращает:
```json
{
'id': id,
'name': name,
'slug': slug
}
```

### 10. `calculate_cost(commision, cost, func) -> int | None`

Возвращает:

int | None

### 11. `get_status_messages(difference) -> dict | None`

Возвращает:

словарь в котором размещены сделки которые имеют статус PAID or CONFIRMED

```json
{id}:{'id': id,'status': status,'timestamp': timestamp}
```



### Туториал как создать cookies.json:
1. качаем расширение cookie editor на ваш браузер. ["chrome cookie editor"](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
2. заходим на playerok.com заходим в расширение и нажимаем export как json
![image](https://github.com/user-attachments/assets/9ce69782-39c3-4c28-8bfe-f93aaa991a35)
3. создаем в папке с api новый файл и называем его cookies.json
4. в него вставляем данные которые мы получили в пункте под №2





### ПРИМЕРЫ ЗАПРОСОВ И ИХ ОТВЕТЫ

### Ответ

```string
id-profile
```

### Запрос get_profile
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="cookies.json")

profile = api.get_profile()
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
profileInterlocutor = 'username2'

chatId = api.on_username_id_get(profileInterlocutor)
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
profileInterlocutor = 'username2'
textMessage = 'Hello!'

ProcessSendMessage = api.on_send_message(profileInterlocutor, textMessage)
```

### Запрос get_balance
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="cookies.json")

balance = api.get_balance()
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

info = api.get_full_info()
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

### Запрос get_product_data
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="api/cookies.json")
link = 'https://playerok.com/products/linkProduct'

Product_Data = api.get_product_data(link)
print(Product_Data)
```

### Ответ

```json
Слишком длиныый.
```


### Запрос copy_product
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="api/cookies.json")
link = 'https://playerok.com/products/linkProduct'

product = api.copy_product(link)
print(product)
```

### Ответ

```json
{
  "title": "title",
  "description": "description",
  "rawprice": rawprice,
  "price": rawprice,
  "attachments": [
    {
      "id": "id",
      "url": "url",
      "__typename": "File"
    }
  ]
}
```


### get_new_messages(self, username, interval=5, max_interval=30) -> dict | None
Получает новые сообщения для указанного пользователя и выводит их в консоль, отслеживая изменения с заданным интервалом.

```python
from playerok_api import PlayerokRequestsApi
api = PlayerokRequestsApi(cookies_file="cookies.json")

messages = api.get_new_messages()

print(messages)
```
- **interval**: Начальный интервал (в секундах) между проверками новых сообщений (по умолчанию 5 секунд).  
- **max_interval**: Максимальный интервал (в секундах), до которого может увеличиваться пауза при отсутствии новых сообщений (по умолчанию 30 секунд).  

Возвращает список новых сообщений, где каждое сообщение — это словарь с полями:  
- `chat_id`: ID чата, в котором появилось новое сообщение.  
- `participant`: Имя собеседника (или "Неизвестно", если имя не удалось определить).  
- `message`: Текст последнего сообщения (или "Сообщение отсутствует", если текст не указан).  
- `date`: Форматированная дата сообщения (например, "Сегодня, 14:30" или "20.04.2025 14:30").  

Сообщения выводятся в консоль с информацией о чате, собеседнике, тексте сообщения и дате. Если новых сообщений нет, интервал между проверками увеличивается на 5 секунд, но не превышает `max_interval`.

---

### get_messages_info(self, unread=False) -> dict | None

```python
from playerok_api import PlayerokRequestsApi
api = PlayerokRequestsApi(cookies_file="cookies.json")

messages = api.get_messages_info()

print(messages)
```

Получает информацию о чатах пользователя, включая количество непрочитанных сообщений и данные о последних сообщениях.

- **username**: Имя пользователя, для которого нужно получить информацию о чатах.  
- **unread**: Флаг, указывающий, нужно ли фильтровать только чаты с непрочитанными сообщениями (по умолчанию `False`).  

Возвращает список чатов, где каждый чат — это словарь с данными:  
- `id`: ID чата.  
- `participants`: Список участников чата (включает имена и ID).  
- `lastMessage`: Информация о последнем сообщении (если есть), включая текст (`text`), дату (`createdAt`) и данные о сделке (`deal`), если она связана с сообщением.  
- `unreadMessagesCounter`: Количество непрочитанных сообщений в чате.  

Метод выводит в консоль общее количество непрочитанных сообщений и информацию о каждом чате (ID, имя собеседника). Если в чате есть последнее сообщение, сохраняет его дату в `self.last_messages` для отслеживания новых сообщений в будущем.

---

### get_lots(self) -> dict | None

```python
from playerok_api import PlayerokRequestsApi
api = PlayerokRequestsApi(cookies_file="cookies.json")

lots = api.get_lots()

print(lots)
```

Получает список лотов пользователя с их идентификаторами и названиями.

- **username**: Имя пользователя, для которого нужно получить список лотов.  

Возвращает список лотов, где каждый лот — это словарь с полями:  
- `id`: ID лота.  
- `name`: Название лота.  

Метод выполняет запрос к API и возвращает только лоты со статусами `APPROVED`, `PENDING_MODERATION` или `PENDING_APPROVAL`. Если запрос не удаётся или возникает ошибка, возвращается пустой список, а ошибка выводится в консоль.

### calculate_cost(self, commision, cost, func) -> int | None

```python
from playerok_api import PlayerokRequestsApi
api = PlayerokRequestsApi(cookies_file="cookies.json")

messages = api.calculate_cost(commision, cost, func)

print(messages)
```

Принимает:

- **commision**: коммисия категории товара (10-20%)

### get_status_messages(difference=300) -> dict | None

```python
from playerok_api import PlayerokRequestsApi
api = PlayerokRequestsApi(cookies_file="cookies.json")

status_messages = api.get_status_messages(difference=300)

print(status_messages)
```


Принимает difference = int (Разница, как давно была оплачена,подтверждена сделка)

Возвращает:

словарь в котором размещены сделки которые имеют статус PAID or CONFIRMED

```json
{id}:{'id': id,'status': status,'timestamp': timestamp}
```

- **cost**: цена за которую будет выставлен товар (raw_price)
- **func**: либо 'upper' (поднятие товара), 'billing' (выставление товара)

Возвращает -> int | None
