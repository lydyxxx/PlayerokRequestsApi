import json, time, tls_requests
from datetime import datetime, date
from urllib.parse import urlparse, parse_qs

globalheaders = {
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'access-control-allow-headers': 'sentry-trace, baggage',
    'apollo-require-preflight': 'true',
    'apollographql-client-name': 'web',
    'content-type': 'application/json',
    'origin': 'https://playerok.com',
    'priority': 'u=1, i',
    'referer': 'https://playerok.com/profile/',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"135.0.7049.115"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="135.0.7049.115", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"19.0.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    'x-timezone-offset': '-180',
}

class PlayerokRequestsApi:
    def __init__(self, cookies_file="cookies.json", logger=False):
        self.cookies = self.load_cookies(cookies_file)
        self.Logging = logger
        self.api_url = "https://playerok.com/graphql"
        self.last_messages = {}
        self.is_first_run = False
        self.username, self.id = self.get_username()

    



    def load_cookies(self, cookies_file):
        cookies_dict = {}
        try:
            with open(cookies_file, "r", encoding="utf-8") as file:
                cookies = json.load(file)
                for cookie in cookies:
                    cookies_dict[cookie["name"]] = cookie["value"]
        except Exception as e:
            print(f"Ошибка при загрузке куков: {e}")
        return cookies_dict
    


    # chats functions

    def on_username_id_get(self, profileusername, username):
        """блять честно хуй знает что тут захуйня но она нужна... вроде как для отправки сообщений надо поменять..."""
        user_id = self.get_id_for_username(profileusername)
        url = "https://playerok.com/graphql"
        params = {
            "operationName": "chats",
            "variables": f'{{"pagination":{{"first":10}},"filter":{{"userId":"{user_id}"}}}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"4ff10c34989d48692b279c5eccf460c7faa0904420f13e380597b29f662a8aa4"}}'
        }

        try:
            response = tls_requests.get(url, params=params, headers=globalheaders, cookies=self.cookies)
            if response.status_code == 200:
                data = response.json()
                errors = data.get("errors", [])
                if errors:
                    errormsg = errors[0].get("message", "Неизвестная ошибка")
                    print(f"Ошибка GraphQL: {errormsg}")
                    return None
                chats_data = data.get("data", {}).get("chats", {})
                edges = chats_data.get("edges", [])
                for edge in edges:
                    node = edge.get("node", {})
                    participants = node.get("participants", [])
                    for participant in participants:
                        if participant.get("username") == username:
                            return node.get("id")
                print(f"Пользователь {username} не найден в списке участников.")
                return None
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None

    def on_send_message(self, username, text):
        """отправить сообщение по Username"""
        chat_id = self.on_username_id_get(self.username, username)
        url = "https://playerok.com/graphql"
        json_data = {
            "operationName": "createChatMessage",
            "variables": {
                "input": {
                    "chatId": chat_id,
                    "text": text,
                },
            },
            "query": "mutation createChatMessage($input: CreateChatMessageInput!, $file: Upload) { createChatMessage(input: $input, file: $file) { ...RegularChatMessage __typename } } fragment RegularChatMessage on ChatMessage { id text createdAt deletedAt isRead isSuspicious isBulkMessaging game { ...RegularGameProfile __typename } file { ...PartialFile __typename } user { ...ChatMessageUserFields __typename } deal { ...ChatMessageItemDeal __typename } item { ...ItemEdgeNode __typename } transaction { ...RegularTransaction __typename } moderator { ...UserEdgeNode __typename } eventByUser { ...ChatMessageUserFields __typename } eventToUser { ...ChatMessageUserFields __typename } isAutoResponse event buttons { ...ChatMessageButton __typename } __typename } fragment RegularGameProfile on GameProfile { id name type slug logo { ...PartialFile __typename } __typename } fragment PartialFile on File { id url __typename } fragment ChatMessageUserFields on UserFragment { ...UserEdgeNode __typename } fragment UserEdgeNode on UserFragment { ...RegularUserFragment __typename } fragment RegularUserFragment on UserFragment { id username role avatarURL isOnline isBlocked rating testimonialCounter createdAt supportChatId systemChatId __typename } fragment ChatMessageItemDeal on ItemDeal { id direction status statusDescription hasProblem user { ...ChatParticipant __typename } testimonial { ...ChatMessageDealTestimonial __typename } item { id name price slug rawPrice sellerType user { ...ChatParticipant __typename } category { id __typename } attachments { ...PartialFile __typename } comment dataFields { ...GameCategoryDataFieldWithValue __typename } obtainingType { ...GameCategoryObtainingType __typename } __typename } obtainingFields { ...GameCategoryDataFieldWithValue __typename } chat { id type __typename } transaction { id statusExpirationDate __typename } statusExpirationDate commentFromBuyer __typename } fragment ChatParticipant on UserFragment { ...RegularUserFragment __typename } fragment ChatMessageDealTestimonial on Testimonial { id status text rating createdAt updatedAt creator { ...RegularUserFragment __typename } moderator { ...RegularUserFragment __typename } user { ...RegularUserFragment __typename } __typename } fragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue { id label type inputType copyable hidden required value __typename } fragment GameCategoryObtainingType on GameCategoryObtainingType { id name description gameCategoryId noCommentFromBuyer instructionForBuyer instructionForSeller sequence feeMultiplier agreements { ...RegularGameCategoryAgreement __typename } props { minTestimonialsForSeller __typename } __typename } fragment RegularGameCategoryAgreement on GameCategoryAgreement { description gameCategoryId gameCategoryObtainingTypeId iconType id sequence __typename } fragment ItemEdgeNode on ItemProfile { ...MyItemEdgeNode ...ForeignItemEdgeNode __typename } fragment MyItemEdgeNode on MyItemProfile { id slug priority status name price rawPrice statusExpirationDate sellerType attachment { ...PartialFile __typename } user { ...UserItemEdgeNode __typename } approvalDate createdAt priorityPosition viewsCounter feeMultiplier __typename } fragment UserItemEdgeNode on UserFragment { ...UserEdgeNode __typename } fragment ForeignItemEdgeNode on ForeignItemProfile { id slug priority status name price rawPrice sellerType attachment { ...PartialFile __typename } user { ...UserItemEdgeNode __typename } approvalDate priorityPosition createdAt viewsCounter feeMultiplier __typename } fragment RegularTransaction on Transaction { id operation direction providerId provider { ...RegularTransactionProvider __typename } user { ...RegularUserFragment __typename } creator { ...RegularUserFragment __typename } status statusDescription statusExpirationDate value fee createdAt props { ...RegularTransactionProps __typename } verifiedAt verifiedBy { ...UserEdgeNode __typename } completedBy { ...UserEdgeNode __typename } paymentMethodId completedAt isSuspicious __typename } fragment RegularTransactionProvider on TransactionProvider { id name fee account { ...RegularTransactionProviderAccount __typename } props { ...TransactionProviderPropsFragment __typename } limits { ...ProviderLimits __typename } paymentMethods { ...TransactionPaymentMethod __typename } __typename } fragment RegularTransactionProviderAccount on TransactionProviderAccount { id value userId __typename } fragment TransactionProviderPropsFragment on TransactionProviderPropsFragment { requiredUserData { ...TransactionProviderRequiredUserData __typename } tooltip __typename } fragment TransactionProviderRequiredUserData on TransactionProviderRequiredUserData { email phoneNumber __typename } fragment ProviderLimits on ProviderLimits { incoming { ...ProviderLimitRange __typename } outgoing { ...ProviderLimitRange __typename } __typename } fragment ProviderLimitRange on ProviderLimitRange { min max __typename } fragment TransactionPaymentMethod on TransactionPaymentMethod { id name fee providerId account { ...RegularTransactionProviderAccount __typename } props { ...TransactionProviderPropsFragment __typename } limits { ...ProviderLimits __typename } __typename } fragment RegularTransactionProps on TransactionPropsFragment { creatorId dealId paidFromPendingIncome paymentURL successURL paymentAccount { id value __typename } paymentGateway alreadySpent exchangeRate __typename } fragment ChatMessageButton on ChatMessageButton { type url text __typename }"
        }
        try:
            response = tls_requests.post(url, headers=globalheaders, cookies=self.cookies, json=json_data)
            if response.status_code == 200:
                data = response.json()
                errors = data.get("errors")
                if errors:
                    print("Ошибка при отправке сообщения:", errors)
                    return None
                create_chat_msg = data.get("data", {}).get("createChatMessage")
                if create_chat_msg:
                    return data
                else:
                    print("Сообщение не было отправлено (ответ не соответствует ожиданиям).")
                    return None
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
        return None

    def get_status_messages(self, difference=300):
        """получить сообщения со статусом надо переписать чтобы смотрело все сообщения а не первую страницу в вкладке сообщения"""
        if self.Logging == True:
            print("start get_status_messages")

        chats = self.fetch_chats(after_cursor=None)
        


        edges = chats['data']['chats']['edges']
        tuple_nodes = []
        for edge in edges:
            try:
                message_created = edge['node']['lastMessage']['createdAt']
                dt = datetime.fromisoformat(message_created.replace('Z', '+00:00'))
                id = edge['node']['id']
                params = {
                    "operationName": "chat",
                    "variables": f'{{"id":"{id}"}}',
                    "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"38efcc58bdc432cc05bc743345e9ef9653a3ca1c0f45db822f4166d0f0cc17c4"}}'
                }

                response = tls_requests.get(self.api_url, params=params, headers=globalheaders, cookies=self.cookies)
                data = json.loads(response.text)

                params2 = {
                    "operationName": "deal",
                    "variables": f'{{"id":"{data['data']['chat']['deals'][0]['id']}"}}',
                    "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"10fb6169572069b90c0fc4997ecd553d96449c573d574295afb70565a0d18198"}}'
                }

                response2 = tls_requests.get(self.api_url, params=params2, headers=globalheaders, cookies=self.cookies)
                data2 = json.loads(response2.text)
                status = data2['data']['deal']['status']
                timestamp = dt.timestamp()
                current_timestamp = time.time()
                if abs(timestamp - current_timestamp) <= difference:
                    if status in ('CONFIRMED', 'SENT', 'ROLLED_BACK', 'PAID'):
                        tuple_nodes.append({'id': data2['data']['deal']['id'], 'status': status, 'timestamp': timestamp})
            except Exception as e:
                if self.Logging == True:
                    print(e)
        return tuple_nodes if tuple_nodes else None

    def get_new_messages(self, interval=5, max_interval=30):
            """получить новые сообщения тоже не понимаю для чего она нужна"""
            username = self.username
            current_interval = interval
            while True:
                if self.Logging == True:
                    print("Начало цикла")
                new_messages = []
                chats = self.get_messages_info(unread=True)  
                for chat_edge in chats:
                    chat = chat_edge["node"]
                    chat_id = chat["id"]
                    last_message = chat.get("lastMessage")
                    if not last_message or not last_message.get("createdAt"):
                        if self.Logging == True:
                            print("Ничего не нашли, продолжаем")
                        continue
                    message_time = last_message["createdAt"]
                    previous_time = self.last_messages.get(chat_id, "1970-01-01T00:00:00.000Z")
                    if message_time > previous_time:
                        self.last_messages[chat_id] = message_time
                        participants = chat.get("participants", [])
                        if participants is None:
                            participants = []
                        participant_username = "Неизвестно"
                        for participant in participants:
                            try:
                                if participant["id"] != self.get_id(username):
                                    participant_username = participant["username"]
                                    break
                            except Exception as e:
                                print(e)
                        message_text = last_message.get("text", "Сообщение отсутствует")
                        dt = datetime.strptime(message_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                        if dt.date() == date.today():
                            formatted_date = f"Сегодня, {dt.strftime('%H:%M')}"
                        else:
                            formatted_date = dt.strftime("%d.%m.%Y %H:%M")
                        new_messages.append({
                            "chat_id": chat_id,
                            "participant": participant_username,
                            "message": message_text,
                            "date": formatted_date
                        })

                if new_messages:
                    current_interval = interval
                else:
                    current_interval = min(current_interval + 5, max_interval)

                time.sleep(current_interval)
                return new_messages  

    def get_messages_info(self, unread=False):
        """получить информацию по всем чатам я думаю не нужная функция либо ее переписать годно надо"""
        username = self.username
        user_id = self.id
        if self.Logging == True:
            print("Начинаем проверку")
        if not user_id:
            print(f"Не удалось найти user_id для пользователя {username}")
            return []

        all_chats = []
        after_cursor = None
        unread_count = 0
        while True:
            data = self.fetch_chats(after_cursor)
            if not data or "data" not in data or "chats" not in data["data"]:
                print("Ошибка: Неверный формат ответа от API")
                break
            chats = data["data"]["chats"]["edges"]
            if not chats:
                break
            for chat_edge in chats:
                chat = chat_edge["node"]
                chat_id = chat["id"]
                chat_unread_count = chat.get("unreadMessagesCounter", 0)
                if unread and chat_unread_count == 0:
                    continue
                unread_count += chat_unread_count
                all_chats.append(chat_edge)
                last_message = chat.get("lastMessage")
                if last_message and last_message.get("createdAt"):
                    self.last_messages[chat_id] = last_message["createdAt"]
            page_info = data["data"]["chats"]["pageInfo"]
            if not page_info["hasNextPage"]:
                break
            after_cursor = page_info["endCursor"]

        if self.Logging == True:
            print(f"Количество непрочитанных сообщений: {unread_count}")

        for chat_edge in all_chats:
            chat = chat_edge["node"]
            chat_id = chat["id"]
            last_message = chat.get("lastMessage")
            deal = last_message.get("deal") if last_message else None
            participants = chat.get("participants", [])
            if participants is None:
                participants = []
            participant_username = "Неизвестно"
            for participant in participants:
                try:
                    if participant["id"] != user_id:
                        participant_username = participant["username"]
                        break
                except Exception as e:
                    print(e)
            if self.Logging == True:
                print(f"Чат с ID {chat_id} (собеседник: {participant_username}):")
            if deal:
                item = deal.get("item", {})
                item_name = item.get("name", "Не указан")
                price = item.get("price", "Не указана")
                status = deal.get("status", "Не указан")
                testimonial = deal.get("testimonial")
                if self.Logging == True:
                    print(f'Сделка на товар "{item_name}" (цена: {price}).')
                    print(f"Статус: {status}.")
                    print("Отзыва нет." if not testimonial else f"Отзыв: {testimonial['text']} (Рейтинг: {testimonial['rating']}).")                    

            else:
                message_text = last_message.get("text", "Сообщение отсутствует") if last_message else "Сообщение отсутствует"
                message_date = last_message.get("createdAt", "Дата неизвестна") if last_message else "Дата неизвестна"
                if message_date != "Дата неизвестна":
                    dt = datetime.strptime(message_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                    if dt.date() == date.today():
                        message_date = f"Сегодня, {dt.strftime('%H:%M')}"
                    else:
                        message_date = dt.strftime("%d.%m.%Y %H:%M")
                if self.Logging == True:
                    print(f"Последнее сообщение: {message_text}")
                    print(f"Дата: {message_date}")

        return all_chats

    def fetch_chats(self, after_cursor=None):
        """захват чатов используется"""
        variables = {
            "pagination": {"first": 10},  
            "filter": {"userId": self.id}
        }
        if after_cursor:
            variables["pagination"]["after"] = after_cursor
        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "4ff10c34989d48692b279c5eccf460c7faa0904420f13e380597b29f662a8aa4"
            }
        }
        params = {
            "operationName": "chats",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions)
        }
        try:
            response = tls_requests.get(self.api_url, headers=globalheaders, params=params, cookies=self.cookies)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None
        
    def fetch_lots(self, after_cursor=None):
        """захват завершенных лотов используется в функции self.get_all_lots"""
    
        variables = {
            "pagination": {"first": 16},  
              "filter": {
                    "userId": self.id,
                    "status": ["DECLINED", "BLOCKED", "EXPIRED", "SOLD", "DRAFT"]
                }
        }
        if after_cursor:
            variables["pagination"]["after"] = after_cursor
        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "d79d6e2921fea03c5f1515a8925fbb816eacaa7bcafe03eb47a40425ef49601e"
            }
        }
        params = {
            "operationName": "items",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions)
        }
        try:
            response = tls_requests.get(self.api_url, headers=globalheaders, params=params, cookies=self.cookies)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None

        
    def fetch_exhibited_lots(self, userid=None, after_cursor=None):
        """захват выставленных лотов"""
        variables = {"pagination":{"first":16},"filter":{"userId":f"{self.id if not userid else userid}","status":["APPROVED"]}}
        if after_cursor:
            variables["pagination"]["after"] = after_cursor
        extensions = {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "d79d6e2921fea03c5f1515a8925fbb816eacaa7bcafe03eb47a40425ef49601e"
            }
        }
        params = {
            "operationName": "items",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions)
        }
        try:
            response = tls_requests.get(self.api_url, headers=globalheaders, params=params, cookies=self.cookies)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return None
        

    def all_exhibited_lots(self, userid=None):
        """все выставленные лоты (можно смотреть у других по userid) не указывая id вы будете смотреть свои лоты"""
        lots = []
        try:
            response = self.fetch_exhibited_lots(userid)
            if not response or 'data' not in response:
                return lots
                
            for edge in response['data']['items']['edges']:
                lots.append(edge)
                
            while True:
                if not response['data']['items']['pageInfo']['hasNextPage'] or not response['data']['items']['pageInfo']['endCursor']:
                    break
                    
                response = self.fetch_exhibited_lots(userid, after_cursor=response['data']['items']['pageInfo']['endCursor'])
                if not response or 'data' not in response:
                    break
                    
                for edge in response['data']['items']['edges']:
                    lots.append(edge)
                    
            return lots  # Return the collected lots instead of the last response
        except Exception as e:
            print(f"Ошибка при получении лотов: {e}")
            return lots

            

            

    # viewer functions
    
    def get_username(self):
        """получить username и id пользователя (используется для получения в начале self.id, self.username)"""
        try:
            json_data = {
    'operationName': 'viewer',
    'variables': {},
    'query': 'query viewer {\n  viewer {\n    ...Viewer\n    __typename\n  }\n}\n\nfragment Viewer on User {\n  id\n  username\n  email\n  role\n  hasFrozenBalance\n  supportChatId\n  systemChatId\n  unreadChatsCounter\n  isBlocked\n  isBlockedFor\n  createdAt\n  lastItemCreatedAt\n  hasConfirmedPhoneNumber\n  canPublishItems\n  profile {\n    id\n    avatarURL\n    testimonialCounter\n    __typename\n  }\n  __typename\n}',
                }
            

            response = tls_requests.post('https://playerok.com/graphql', cookies=self.cookies, headers=globalheaders, json=json_data)
            try:

                #print(response.text)

                data = response.json()  
                viewer = data.get('data', {}).get('viewer', {})
                
                username = viewer.get('username', '')
                id = viewer.get('id', '')
                if not username:
                    raise ValueError("Username not found")

                return username, id
            except Exception as e:
                print(f'Unsolved problem(Please pass this error to the API owner.) - ERROR: {e}')


        except ValueError as e:
            print(f"Ошибка данных: {e}")
            return ''
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return ''


    def get_all_lots(self, search_filter: str = None) -> list[dict]:
        """получить информацию по всем завершённым лотам"""
        after_cursor = None
        all_lots = []

        while True:
            response = self.fetch_lots(after_cursor=after_cursor)
            
            if not response or "data" not in response or "items" not in response["data"]:
                break

            items = response["data"]["items"]
            edges = items.get("edges", [])
            page_info = items.get("pageInfo", {})

            for edge in edges:
                if not edge.get("node"):
                    continue
                    
                if search_filter:
                    node = edge["node"]
                    if any(search_filter.lower() in str(value).lower() 
                        for value in node.values() 
                        if isinstance(value, (str, int, float))):
                        all_lots.append(node)
                else:
                    all_lots.append(edge["node"])

            if not page_info.get("hasNextPage") or not page_info.get("endCursor"):
                break

            after_cursor = page_info["endCursor"]

        return all_lots


    def copy_product(self, link):

        """получить информацию для выставления товара через ссылку"""

        if self.Logging == True:
            print("Начинаем копировать продукт")
        url = "https://playerok.com/graphql"
        slug = link.replace("https://playerok.com/products", "").split('?')[0].strip('/')

        params = {
            "operationName": "item",
            "variables": f'{{"slug":"{slug}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}'
        }

        try:
            response = tls_requests.get(url, params=params, headers=globalheaders, cookies=self.cookies)
            if response.status_code == 200:
                data = json.loads(response.text)
                errors = data.get("errors", [])
                if errors:
                    errormsg = errors[0].get("message", "Неизвестная ошибка")
                    print(f"Ошибка GraphQL: {errormsg}")
                    return None
                product_data = {
                    "title": data["data"]["item"]["name"],
                    "description": data["data"]["item"]["description"],
                    "rawprice": data["data"]["item"]["rawPrice"],
                    "price": data["data"]["item"]["price"],
                    "attachments": data["data"]["item"]["attachments"]
                }

                return product_data
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None

    def increase_item_priority(self, item_id):
        """поднять товар по айди"""
        url = "https://playerok.com/graphql"
        json_data = {
        "operationName": "increaseItemPriorityStatus",
        "variables": {
            "input": {
            "priorityStatuses": [
                "1f00f21b-7768-62a0-296f-75a31ee8ce72"
            ],
            "transactionProviderId": "LOCAL",
            "transactionProviderData": {
                "paymentMethodId": None
            },
            "itemId": f"{item_id}"
            }
        },
        "query": "mutation increaseItemPriorityStatus($input: PublishItemInput!) {\n  increaseItemPriorityStatus(input: $input) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  sequence\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}"
        }
        try:
            response = tls_requests.post(url, headers=globalheaders, cookies=self.cookies, json=json_data)
            if response.status_code == 200:
                data = response.json()
                print(data)
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
        return None

    def refill_item(self, item_id):
        """возобновить товар по id (он завершен)"""
        url = "https://playerok.com/graphql"
        json_data = {
        "operationName": "publishItem",
        "variables": {
            "input": {
            "priorityStatuses": [
                "1f00f21b-7768-62a0-296f-75a31ee8ce72"
            ],
            "transactionProviderId": "LOCAL",
            "transactionProviderData": {
                "paymentMethodId": None
            },
            "itemId": f"{item_id}"
            }
        },
        "query": "mutation publishItem($input: PublishItemInput!) {\n  publishItem(input: $input) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...MinimalGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalGameCategoryAgreement on GameCategoryAgreement {\n  description\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}"
        }
        try:
            response = tls_requests.post(url, headers=globalheaders, cookies=self.cookies, json=json_data)
            if response.status_code == 200:
                data = response.json()
                print(data)
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
        return None

    def get_product_data(self, link):
        """получить информацию о товаре через ссылку"""
        url = "https://playerok.com/graphql"
        slug = link.replace("https://playerok.com/products", "").split('?')[0].strip('/')

        params = {
            "operationName": "item",
            "variables": f'{{"slug":"{slug}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}'
        }

        try:
            response = tls_requests.get(url, params=params, headers=globalheaders, cookies=self.cookies)
            if response.status_code == 200:
                data = json.loads(response.text)
                errors = data.get("errors", [])
                if errors:
                    errormsg = errors[0].get("message", "Неизвестная ошибка")
                    print(f"Ошибка GraphQL: {errormsg}")
                    return None
                product_data = data

                return product_data
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None
    

    def get_item_positioninfind(self, item_slug):
        """получить позицию предмета на рынке по slug"""
        params = {
            'operationName': 'item',
            'variables': f'{{"slug":"{item_slug}"}}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}',
        }
        response = tls_requests.get('https://playerok.com/graphql', params=params, cookies=self.cookies, headers=globalheaders)
        data = response.json()
        sequence = data['data']['item']['sequence']
        return sequence

 

    # user functions

    def get_id_for_username(self, username):
        """получить айди пользователя по никнейму"""
        url = "https://playerok.com/graphql"
        params = {
            "operationName": "user",
            "variables": f'{{"username":"{username}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"6dff0b984047e79aa4e416f0f0cb78c5175f071e08c051b07b6cf698ecd7f865"}}'
        }
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "access-control-allow-headers": "sentry-trace, baggage",
            "apollo-require-preflight": "true",
            "apollographql-client-name": "web",
            "referer": "https://playerok.com/profile/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }
        try:
            response = tls_requests.get(url, params=params, headers=headers, cookies=self.cookies)
            if response.status_code == 200:
                print("Запрос успешен!")
                data = json.loads(response.text)
                errors = data.get("errors", [])
                if errors:
                    errormsg = errors[0].get("message", "Неизвестная ошибка")
                    print(f"Ошибка GraphQL: {errormsg}")
                    return None
                user_data = data["data"]["user"]
                user_id = user_data['id']
                return user_id
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None

    def get_balance(self):
        """получить баланс аккаунта из куки"""
        if self.Logging == True:
            print("Начало проверки")
        username = self.username
        url = "https://playerok.com/graphql"
        params = {
            "operationName": "user",
            "variables": f'{{"username":"{username}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"6dff0b984047e79aa4e416f0f0cb78c5175f071e08c051b07b6cf698ecd7f865"}}'
        }

        try:
            response = tls_requests.get(url, params=params, headers=globalheaders, cookies=self.cookies)
            print(response.text)
            if response.status_code == 200:
                data = json.loads(response.text)
                errors = data.get("errors", [])
                if errors:
                    errormsg = errors[0].get("message", "Неизвестная ошибка")
                    print(f"Ошибка GraphQL: {errormsg}")
                    return None
                user_data = data["data"]["user"]
                balance = {
                    'AllBalance': user_data["balance"]["value"],
                    'available': user_data["balance"]["available"],
                    'pendingIncome': user_data["balance"]["pendingIncome"],
                    'frozen': user_data["balance"]["frozen"]
                }
                return balance
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None


    def get_full_info(self):
        """получить полную информацию о профиле из личных куки"""
        username = self.username
        url = "https://playerok.com/graphql"
        params = {
            "operationName": "user",
            "variables": f'{{"username":"{username}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"6dff0b984047e79aa4e416f0f0cb78c5175f071e08c051b07b6cf698ecd7f865"}}'
        }

        try:
            response = tls_requests.get(url, params=params, headers=globalheaders, cookies=self.cookies)
            if response.status_code == 200:
                data = json.loads(response.text)
                errors = data.get("errors", [])
                if errors:
                    errormsg = errors[0].get("message", "Неизвестная ошибка")
                    print(f"Ошибка GraphQL: {errormsg}")
                    return None
                user_data = data["data"]["user"]
                return user_data
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None

    def get_profile(self):
        """получить информацию о профиле из личных cookie"""
        username = self.username
        url = "https://playerok.com/graphql"
        params = {
            "operationName": "user",
            "variables": f'{{"username":"{username}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"6dff0b984047e79aa4e416f0f0cb78c5175f071e08c051b07b6cf698ecd7f865"}}'
        }

        try:
            response = tls_requests.get(url, params=params, headers=globalheaders, cookies=self.cookies)
            if response.status_code == 200:
                data = json.loads(response.text)
                errors = data.get("errors", [])
                if errors:
                    errormsg = errors[0].get("message", "Неизвестная ошибка")
                    print(f"Ошибка GraphQL: {errormsg}")
                    return None
                user_data = data["data"]["user"]
                user_id = user_data['id']
                nickname = user_data["username"]
                testimonial_count = user_data["profile"]["testimonialCounter"]
                total_items = user_data["stats"]["items"]["total"]
                finished_items = user_data["stats"]["items"]["finished"]
                active_items = total_items - finished_items
                purchases_total = user_data["stats"]["deals"]["incoming"]["total"]
                sales_total = user_data["stats"]["deals"]["outgoing"]["total"]
                return (
                    nickname,
                    testimonial_count,
                    total_items,
                    purchases_total,
                    sales_total,
                    active_items,
                    finished_items,
                )
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None
        
    # other functions

    def get_unread_messages(self):
        """"возвращает int не прочитанных сообщений"""
        chats = self.fetch_chats()
        unread_messages = 0
        for chat in chats['data']['chats']['edges']:
            unread_messages += int(chat['node']['unreadMessagesCounter'])
        return unread_messages
    
    # deals function

    def deal_confirm(self, id):
        """подтвердить сделку по id"""
        json_data = {
        "operationName": "updateDeal",
        "variables": {
            "input": {
            "id": f"{id}",
            "status": "SENT"
            }
        },
        "query": "mutation updateDeal($input: UpdateItemDealInput!) {\n  updateDeal(input: $input) {\n    ...RegularItemDeal\n    __typename\n  }\n}\n\nfragment RegularItemDeal on ItemDeal {\n  id\n  status\n  direction\n  statusExpirationDate\n  statusDescription\n  obtaining\n  hasProblem\n  reportProblemEnabled\n  completedBy {\n    ...MinimalUserFragment\n    __typename\n  }\n  props {\n    ...ItemDealProps\n    __typename\n  }\n  prevStatus\n  completedAt\n  createdAt\n  logs {\n    ...ItemLog\n    __typename\n  }\n  transaction {\n    ...ItemDealTransaction\n    __typename\n  }\n  user {\n    ...UserEdgeNode\n    __typename\n  }\n  chat {\n    ...RegularChatId\n    __typename\n  }\n  item {\n    ...PartialDealItem\n    __typename\n  }\n  testimonial {\n    ...RegularItemDealTestimonial\n    __typename\n  }\n  obtainingFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  commentFromBuyer\n  __typename\n}\n\nfragment MinimalUserFragment on UserFragment {\n  id\n  username\n  role\n  __typename\n}\n\nfragment ItemDealProps on ItemDealProps {\n  autoConfirmPeriod\n  __typename\n}\n\nfragment ItemLog on ItemLog {\n  id\n  event\n  createdAt\n  user {\n    ...UserEdgeNode\n    __typename\n  }\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment ItemDealTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  value\n  createdAt\n  paymentMethodId\n  statusExpirationDate\n  __typename\n}\n\nfragment RegularChatId on Chat {\n  id\n  __typename\n}\n\nfragment PartialDealItem on Item {\n  ...PartialDealMyItem\n  ...PartialDealForeignItem\n  __typename\n}\n\nfragment PartialDealMyItem on MyItem {\n  id\n  slug\n  priority\n  status\n  name\n  price\n  priorityPrice\n  rawPrice\n  statusExpirationDate\n  sellerType\n  approvalDate\n  createdAt\n  priorityPosition\n  viewsCounter\n  feeMultiplier\n  comment\n  attachments {\n    ...RegularFile\n    __typename\n  }\n  user {\n    ...UserEdgeNode\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  category {\n    ...MinimalGameCategory\n    __typename\n  }\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...MinimalGameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment RegularFile on File {\n  id\n  url\n  filename\n  mime\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment MinimalGameCategory on GameCategory {\n  id\n  slug\n  name\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment MinimalGameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment PartialDealForeignItem on ForeignItem {\n  id\n  slug\n  priority\n  status\n  name\n  price\n  rawPrice\n  sellerType\n  approvalDate\n  priorityPosition\n  createdAt\n  viewsCounter\n  feeMultiplier\n  comment\n  attachments {\n    ...RegularFile\n    __typename\n  }\n  user {\n    ...UserEdgeNode\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  category {\n    ...MinimalGameCategory\n    __typename\n  }\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...MinimalGameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment RegularItemDealTestimonial on Testimonial {\n  id\n  status\n  text\n  rating\n  createdAt\n  updatedAt\n  creator {\n    ...RegularUserFragment\n    __typename\n  }\n  moderator {\n    ...RegularUserFragment\n    __typename\n  }\n  user {\n    ...RegularUserFragment\n    __typename\n  }\n  __typename\n}"
        }
        try:
            response = tls_requests.post(self.api_url, headers=globalheaders, cookies=self.cookies, json=json_data)
            return response.json()
        except Exception as e:
            pass

    def get_actual_deals(self):
        """"получить список актуальных сделок который оплачены"""
        params = {
            "operationName": "countDeals",
            "variables": json.dumps({
                "filter": {
                    "userId": self.id,
                    "direction": "OUT",
                    "status": ["PAID"]
                }
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "1e2605594b38041bb7a5466a9cab994a169725d7b69aae3b7ee185d0b7fc33c2"
                }
            })
        }



        try:
            response = tls_requests.get(
                self.api_url,
                params=params,
                headers=globalheaders,
                cookies=self.cookies
            )
            response.raise_for_status() 
            data = response.json()
            return data 
        except:
            pass
