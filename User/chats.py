import json
import time
from datetime import datetime, date
from urllib.parse import urlparse, parse_qs
import tls_requests
from PlayerokRequestsApi.utils import globalheaders, load_cookies

class PlayerokChatsApi:
    def __init__(self, cookies_file="cookies.json", logger=False):
        self.cookies = load_cookies(cookies_file)
        self.Logging = logger
        self.api_url = "https://playerok.com/graphql"
        self.last_messages = {}
        self.username, self.id = self.get_username()

    def on_username_id_get(self, profileusername, username):
        """блять честно хуй знает что тут захуйня но она нужна... вроде как для отправки сообщений надо поменять..."""
        user_id = self.get_id_for_username(profileusername)
        params = {
            "operationName": "chats",
            "variables": f'{{"pagination":{{"first":10}},"filter":{{"userId":"{user_id}"}}}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"4ff10c34989d48692b279c5eccf460c7faa0904420f13e380597b29f662a8aa4"}}'
        }

        try:
            response = tls_requests.get(self.api_url, params=params, headers=globalheaders, cookies=self.cookies)
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
            response = tls_requests.post(self.api_url, headers=globalheaders, cookies=self.cookies, json=json_data)
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
        if self.Logging:
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
                if self.Logging:
                    print(e)
        return tuple_nodes if tuple_nodes else None

    def get_new_messages(self, interval=5, max_interval=30):
        """получить новые сообщения тоже не понимаю для чего она нужна"""
        username = self.username
        current_interval = interval
        while True:
            if self.Logging:
                print("Начало цикла")
            new_messages = []
            chats = self.get_messages_info(unread=True)
            for chat_edge in chats:
                chat = chat_edge["node"]
                chat_id = chat["id"]
                last_message = chat.get("lastMessage")
                if not last_message or not last_message.get("createdAt"):
                    if self.Logging:
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
        if self.Logging:
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

        if self.Logging:
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
            if self.Logging:
                print(f"Чат с ID {chat_id} (собеседник: {participant_username}):")
            if deal:
                item = deal.get("item", {})
                item_name = item.get("name", "Не указан")
                price = item.get("price", "Не указана")
                status = deal.get("status", "Не указан")
                testimonial = deal.get("testimonial")
                if self.Logging:
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
                if self.Logging:
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

    def get_unread_messages(self):
        """возвращает int не прочитанных сообщений"""
        chats = self.fetch_chats()
        unread_messages = 0
        for chat in chats['data']['chats']['edges']:
            unread_messages += int(chat['node']['unreadMessagesCounter'])
        return unread_messages