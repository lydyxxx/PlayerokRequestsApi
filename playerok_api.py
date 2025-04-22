import json, time, tls_requests
from datetime import datetime, date
from urllib.parse import urlparse, parse_qs



globalheaders = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'access-control-allow-headers': 'sentry-trace, baggage',
    'apollo-require-preflight': 'true',
    'apollographql-client-name': 'web',
    'origin': 'https://playerok.com',
    'priority': 'u=1, i',
    'referer': 'https://playerok.com/chats/',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'x-timezone-offset': '480',
}

class PlayerokRequestsApi:
    def __init__(self, cookies_file="cookies.json"):
        self.cookies = self.load_cookies(cookies_file)
        self.api_url = "https://playerok.com/graphql"
        self.last_messages = {}
        self.is_first_run = False
        self.username, self.id = self.get_username()

    



    def load_cookies(self, cookies_file):
        """Загружает куки из JSON-файла и возвращает словарь с куками."""
        cookies_dict = {}
        try:
            with open(cookies_file, "r", encoding="utf-8") as file:
                cookies = json.load(file)
                for cookie in cookies:
                    cookies_dict[cookie["name"]] = cookie["value"]
        except Exception as e:
            print(f"Ошибка при загрузке куков: {e}")
        return cookies_dict
    

    def get_new_messages(self, interval=5, max_interval=30):
            username = self.username
            current_interval = interval
            while True:
                new_messages = []
                chats = self.get_messages_info(unread=True)  
                for chat_edge in chats:
                    chat = chat_edge["node"]
                    chat_id = chat["id"]
                    last_message = chat.get("lastMessage")
                    if not last_message or not last_message.get("createdAt"):
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
        username = self.username
        user_id = self.id
        if not user_id:
            print(f"Не удалось найти user_id для пользователя {username}")
            return []

        def fetch_chats(after_cursor=None):
            variables = {
                "pagination": {"first": 10},  
                "filter": {"userId": user_id}
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

        all_chats = []
        after_cursor = None
        unread_count = 0
        while True:
            data = fetch_chats(after_cursor)
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

        #print(f"Количество непрочитанных сообщений: {unread_count}")

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
            #print(f"Чат с ID {chat_id} (собеседник: {participant_username}):")
            if deal:
                item = deal.get("item", {})
                item_name = item.get("name", "Не указан")
                price = item.get("price", "Не указана")
                status = deal.get("status", "Не указан")
                testimonial = deal.get("testimonial")
                #print(f'Сделка на товар "{item_name}" (цена: {price}).')
                #print(f"Статус: {status}.")
                #print("Отзыва нет." if not testimonial else f"Отзыв: {testimonial['text']} (Рейтинг: {testimonial['rating']}).")
            else:
                message_text = last_message.get("text", "Сообщение отсутствует") if last_message else "Сообщение отсутствует"
                message_date = last_message.get("createdAt", "Дата неизвестна") if last_message else "Дата неизвестна"
                if message_date != "Дата неизвестна":
                    dt = datetime.strptime(message_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                    if dt.date() == date.today():
                        message_date = f"Сегодня, {dt.strftime('%H:%M')}"
                    else:
                        message_date = dt.strftime("%d.%m.%Y %H:%M")
                #print(f"Последнее сообщение: {message_text}")
                #print(f"Дата: {message_date}")
            #print()

        return all_chats

    
    def get_username(self):
        try:
            json_data = {
        'operationName': 'viewer',
        'variables': {},
        'query': 'query viewer {\n  viewer {\n    ...Viewer\n    __typename\n  }\n}\n\nfragment Viewer on User {\n  id\n  username\n  email\n  role\n  hasFrozenBalance\n  supportChatId\n  systemChatId\n  unreadChatsCounter\n  isBlocked\n  isBlockedFor\n  createdAt\n  lastItemCreatedAt\n  hasConfirmedPhoneNumber\n  canPublishItems\n  profile {\n    id\n    avatarURL\n    testimonialCounter\n    __typename\n  }\n  __typename\n}',
    }

            response = tls_requests.post('https://playerok.com/graphql', cookies=self.cookies, headers=globalheaders, json=json_data)

            data = response.json()  
            viewer = data.get('data', {}).get('viewer', {})
            
            username = viewer.get('username', '')
            id = viewer.get('id', '')
            if not username:
                raise ValueError("Username not found")

            return username, id


        except ValueError as e:
            print(f"Ошибка данных: {e}")
            return ''
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return ''


    def get_item_positioninfind(self, item_slug):
        params = {
            'operationName': 'item',
            'variables': f'{{"slug":"{item_slug}"}}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}',
        }
        response = tls_requests.get('https://playerok.com/graphql', params=params, cookies=self.cookies, headers=globalheaders)
        data = response.json()
        sequence = data['data']['item']['sequence']
        return sequence

    def get_lots(self, slug_only=False):
        username = self.username

        try:
            user_id = self.id
            if not user_id:
                raise ValueError("Invalid user_id")

            params = {
                'operationName': 'items',
                'variables': json.dumps({
                    'pagination': {'first': 24},
                    'filter': {
                        'userId': user_id,
                        'status': ['APPROVED', 'PENDING_MODERATION', 'PENDING_APPROVAL']
                    }
                }),
                'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"d79d6e2921fea03c5f1515a8925fbb816eacaa7bcafe03eb47a40425ef49601e"}}',
            }

            response = tls_requests.get('https://playerok.com/graphql', params=params, cookies=self.cookies, headers=globalheaders)
            response.raise_for_status()

            data = response.json()

            lots = []
            edges = data.get('data', {}).get('items', {}).get('edges', [])
            for edge in edges:
                node = edge.get('node', {})
                lot = {
                    'id': node.get('id', ''),
                    'name': node.get('name', ''),
                    'slug': node.get('slug', '') 
                }
                lots.append(lot)

            if slug_only:
                return [lot['slug'] for lot in lots]  
            return lots

        except Exception as e:
            print(f"Ошибка при получении лотов: {e}")
            return [] if not slug_only else []

        except Exception as e:
            print(f"Error fetching or parsing lots: {e}")
            return []



    def get_balance(self):
        username = self.username
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
        username = self.username
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
        username = self.username
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

    def get_product_data(self, link):
        url = "https://playerok.com/graphql"
        slug = link.replace("https://playerok.com/products", "").split('?')[0].strip('/')

        params = {
            "operationName": "item",
            "variables": f'{{"slug":"{slug}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}'
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
        
    def copy_product(self, link):
        url = "https://playerok.com/graphql"
        slug = link.replace("https://playerok.com/products", "").split('?')[0].strip('/')

        params = {
            "operationName": "item",
            "variables": f'{{"slug":"{slug}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}'
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

    def on_send_message(self, text):
        chat_id = self.on_username_id_get()
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

    

    def on_username_id_get(self):
        username = self.username
        user_id = self.id
        url = "https://playerok.com/graphql"
        params = {
            "operationName": "chats",
            "variables": f'{{"pagination":{{"first":10}},"filter":{{"userId":"{user_id}"}}}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"4ff10c34989d48692b279c5eccf460c7faa0904420f13e380597b29f662a8aa4"}}'
        }
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "access-control-allow-headers": "sentry-trace, baggage",
            "apollo-require-preflight": "true",
            "apollographql-client-name": "web",
            "referer": "https://playerok.com/chats/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }
        try:
            response = tls_requests.get(url, params=params, headers=headers, cookies=self.cookies)
            if response.status_code == 200:
                try:
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
                            try:
                                if participant.get("username") == username:
                                    return node.get("id")
                            except Exception as e:
                                print(f'Ошибка {e}')    
                    print(f"Пользователь {username} не найден в списке участников.")
                    return None
                except Exception as e:
                    print(f'Ошибка при запросе!{e}')
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None
