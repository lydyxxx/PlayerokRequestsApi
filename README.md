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

```pip install tls_requests```

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

### 5. `get_balance(myProfile) -> dict | None`
Возвращает словарь из 3 значений с данными баланса вашего профиля:
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
   
### 6. `get_full_info(myProfile) -> dict | None`
Возвращает полный словарь всей информации о профиле.

### 7. `get_product_data(link) -> dict | None`
Возвращает полный словарь всей информации о товаре.

### 8. `copy_product(link) -> dict | None`
Возвращает словарь информации о товаре нужной для выставления товара:
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


### Туториал как создать cookies.json:
1. качаем расширение cookie editor на ваш браузер. ["chrome cookie editor"](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
2. заходим на playerok.com заходим в расширение и нажимаем export как json
![image](https://github.com/user-attachments/assets/9ce69782-39c3-4c28-8bfe-f93aaa991a35)
3. создаем в папке с api новый файл и называем его cookies.json
4. в него вставляем данные которые мы получили в пункте под №2





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

### Запрос get_product_data
```python
from playerok_api import PlayerokRequestsApi

api = PlayerokRequestsApi(cookies_file="api/cookies.json")
link = 'https://playerok.com/products/563fd7dbd13d-spider-man-2-99-000-igr-v-stim-podarkichek-opisanie'

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
link = 'https://playerok.com/products/563fd7dbd13d-spider-man-2-99-000-igr-v-stim-podarkichek-opisanie'

product = api.copy_product(link)
print(product)
```

### Ответ

```json
{
  "title": "🎁Spider-Man 2 + 99 000 ИГР В СТИМ🎁+ПОДАРКИ❗ЧЕК ОПИСАНИЕ❗",
  "description": "📋 После покупки вы получите:\nДоступ к базе с 99.000 играми в том числе: Spider Man 2 MiSide, Hogwarts Legacy, Garry's Mod, Among Us, Planet Coaster, Left 4 Dead, Tomb Raider, Little Nightmares, Injustice: Gods Among Us Ultimate Edition, Forza Horizon 5, Wallpaper Engine, Grand Theft Auto V, The Forest, Assetto Corsa, Red Dead Redemption 2, Friday the 13th: The Game, Inside the Backrooms, ARK: Survival Of The Fittest, Metro 2033, The Elder Scrolls V: Skyrim, Goat Simulator, Portal, The Last Of Us, Phasmophobia ,Baldur's Gate 3, GTA V, GTA IV, Mafia: Definitive Edition, Mafia II (Classic), Mafia II: Definitive Edition, Detroit, Hello Neighbor, Batman Arkham Knight, Borderlands2 , Borderlands 3, Dying Light, Dying Light 2, My Summer Car, Spider Man Remastered, Spider-man Miles Morales, Atomic Heart и многих других\n\n🎉 Аккаунты пополняются почти каждый день, а бывает и чаще!\n\n📋 Так-же при покупке товара вы получаете:\n1. Подарки на сумму 1000р+\n2. Возможность найти на купленных аккаунтах доп.игры\n3. Помощь и поддержку\n4. Оффлайн активацию аккаунтов\n\n❗️ Важно перед покупкой:\nВы покупаете общие оффлайн аккаунты, а это значит что доступ к этим аккаунтам могут иметь другие пользователи, а так-же вы не можете сменить данные от аккаунтов. Так-же игры указанные на обложке могут не соответствовать содержимому аккаунтов, но вы можете попросить продавца и мы постараемся добавить вашу игру\n\n❗️ Товар не подлежит возврату ибо после покупки вы сразу получаете данные от аккаунта и подарок",
  "rawprice": 499,
  "price": 90,
  "attachments": [
    {
      "id": "1f00c67f-b5f3-6190-3f89-afe4a8010392",
      "url": "https://i.playerok.com/P1OzOnCcZ83bv2ohfI2S2VwXTypH00gxo_J3tWMkZk4/wm:0.8:soea:5:2:0.2/rs:fill:0:1000:0/g:no/quality:99/czM6Ly9wbGF5ZXJvay8vaW1hZ2VzLzFmMDBjNjdmLWI1ZjMtNjE5MC0zZjg5LWFmZTRhODAxMDM5Mi5qcGc.jpg",
      "__typename": "File"
    }
  ]
}
```
