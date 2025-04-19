import json
import tls_requests

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


    def get_balance(self, username):
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
                balance = {
                    'AllBalance': user_data["balance"]["value"],
                    'available': user_data["balance"]["available"],
                    'pendingIncome': user_data["balance"]["pendingIncome"]
                }
                return balance
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None


    def get_full_info(self, username):
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
                return user_data
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None

    def get_id(self, username):
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

    def get_profile(self, username):
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
                nickname = user_data["username"]
                testimonial_count = user_data["profile"]["testimonialCounter"]
                total_items = user_data["stats"]["items"]["total"]
                finished_items = user_data["stats"]["items"]["finished"]
                active_items = total_items - finished_items
                purchases_total = user_data["stats"]["deals"]["incoming"]["total"]
                sales_total = user_data["stats"]["deals"]["outgoing"]["total"]
                print(user_id)
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

    def on_send_message(self, profileusername, username, text):
        chat_id = self.on_username_id_get(profileusername, username)
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

    def on_username_id_get(self, profileusername, username):
        user_id = self.get_id(profileusername)
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
