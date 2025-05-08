import json
import tls_requests
from PlayerokRequestsApi.utils import globalheaders, load_cookies

class PlayerokUsersApi:
    def __init__(self, cookies_file="cookies.json", logger=False):
        self.cookies = load_cookies(cookies_file)
        self.Logging = logger
        self.api_url = "https://playerok.com/graphql"
        self.username, self.id = self.get_username()

    def get_username(self):
        """получить username и id пользователя (используется для получения в начале self.id, self.username)"""
        try:
            json_data = {
                'operationName': 'viewer',
                'variables': {},
                'query': 'query viewer {\n  viewer {\n    ...Viewer\n    __typename\n  }\n}\n\nfragment Viewer on User {\n  id\n  username\n  email\n  role\n  hasFrozenBalance\n  supportChatId\n  systemChatId\n  unreadChatsCounter\n  isBlocked\n  isBlockedFor\n  createdAt\n  lastItemCreatedAt\n  hasConfirmedPhoneNumber\n  canPublishItems\n  profile {\n    id\n    avatarURL\n    testimonialCounter\n    __typename\n  }\n  __typename\n}',
            }
            response = tls_requests.post(self.api_url, cookies=self.cookies, headers=globalheaders, json=json_data)
            try:
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
            return '', ''
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            return '', ''

    def get_id_for_username(self, username):
        """получить айди пользователя по никнейму"""
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
            response = tls_requests.get(self.api_url, params=params, headers=headers, cookies=self.cookies)
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
        if self.Logging:
            print("Начало проверки")
        username = self.username
        params = {
            "operationName": "user",
            "variables": f'{{"username":"{username}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"6dff0b984047e79aa4e416f0f0cb78c5175f071e08c051b07b6cf698ecd7f865"}}'
        }

        try:
            response = tls_requests.get(self.api_url, params=params, headers=globalheaders, cookies=self.cookies)
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
        params = {
            "operationName": "user",
            "variables": f'{{"username":"{username}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"6dff0b984047e79aa4e416f0f0cb78c5175f071e08c051b07b6cf698ecd7f865"}}'
        }

        try:
            response = tls_requests.get(self.api_url, params=params, headers=globalheaders, cookies=self.cookies)
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
        params = {
            "operationName": "user",
            "variables": f'{{"username":"{username}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"6dff0b984047e79aa4e416f0f0cb78c5175f071e08c051b07b6cf698ecd7f865"}}'
        }

        try:
            response = tls_requests.get(self.api_url, params=params, headers=globalheaders, cookies=self.cookies)
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