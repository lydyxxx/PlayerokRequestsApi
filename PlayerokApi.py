import json
import tls_requests


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

    def get_profile(self, username):
        """Делает GET-запрос к API GraphQL, 
        передавая operationName/variables/extensions в query-параметрах.
        Парсит некоторые поля из JSON-ответа.
        """
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
                nickname = user_data["username"]
                testimonial_count = user_data["profile"]["testimonialCounter"]

                total_items = user_data["stats"]["items"]["total"]
                finished_items = user_data["stats"]["items"]["finished"]
                active_items = total_items - finished_items

                purchases_total = user_data["stats"]["deals"]["incoming"]["total"]
                sales_total = user_data["stats"]["deals"]["outgoing"]["total"]

                return nickname, testimonial_count, total_items, purchases_total, sales_total, active_items, finished_items   
            else:
                print(f"Ошибка {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None


if __name__ == "__main__":
    api = PlayerokRequestsApi()
    username = 'username'
    result = api.get_profile(username)

    if result:
        (nickname, 
         testimonial_count, 
         total_items, 
         purchases_total, 
         sales_total, 
         active_items, 
         finished_items) = result

        print("Парсинг результата:")
        print(f"Никнейм: {nickname}")
        print(f"Количество отзывов: {testimonial_count}")
        print(f"Всего товаров: {total_items}")
        print(f"Количество покупок: {purchases_total}")
        print(f"Количество продаж: {sales_total}")
        print(f"Активные товары: {active_items}")
        print(f"Завершенные товары: {finished_items}")
    else:
        print('Ничего не найдено или возникла ошибка.')
