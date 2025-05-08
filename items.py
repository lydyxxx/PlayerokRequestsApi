import json
import tls_requests
from PlayerokRequestsApi.utils import globalheaders, load_cookies

class PlayerokItemsApi:
    def __init__(self, cookies_file="cookies.json", logger=False):
        self.cookies = load_cookies(cookies_file)
        self.Logging = logger
        self.api_url = "https://playerok.com/graphql"
        self.username, self.id = self.get_username()

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
        variables = {"pagination": {"first": 16}, "filter": {"userId": f"{self.id if not userid else userid}", "status": ["APPROVED"]}}
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

            return lots
        except Exception as e:
            print(f"Ошибка при получении лотов: {e}")
            return lots

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
        if self.Logging:
            print("Начинаем копировать продукт")
        slug = link.replace("https://playerok.com/products", "").split('?')[0].strip('/')
        params = {
            "operationName": "item",
            "variables": f'{{"slug":"{slug}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}'
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
        json_data = {
            "operationName": "increaseItemPriorityStatus",
            "variables": {
                "input": {
                    "priorityStatuses": ["1f00f21b-7768-62a0-296f-75a31ee8ce72"],
                    "transactionProviderId": "LOCAL",
                    "transactionProviderData": {"paymentMethodId": None},
                    "itemId": f"{item_id}"
                }
            },
            "query": "mutation increaseItemPriorityStatus($input: PublishItemInput!) {\n  increaseItemPriorityStatus(input: $input) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  sequence\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}"
        }
        try:
            response = tls_requests.post(self.api_url, headers=globalheaders, cookies=self.cookies, json=json_data)
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
        json_data = {
            "operationName": "publishItem",
            "variables": {
                "input": {
                    "priorityStatuses": ["1f00f21b-7768-62a0-296f-75a31ee8ce72"],
                    "transactionProviderId": "LOCAL",
                    "transactionProviderData": {"paymentMethodId": None},
                    "itemId": f"{item_id}"
                }
            },
            "query": "mutation publishItem($input: PublishItemInput!) {\n  publishItem(input: $input) {\n    ...RegularItem\n    __typename\n  }\n}\n\nfragment RegularItem on Item {\n  ...RegularMyItem\n  ...RegularForeignItem\n  __typename\n}\n\nfragment RegularMyItem on MyItem {\n  ...ItemFields\n  prevPrice\n  priority\n  sequence\n  priorityPrice\n  statusExpirationDate\n  comment\n  viewsCounter\n  statusDescription\n  editable\n  statusPayment {\n    ...StatusPaymentTransaction\n    __typename\n  }\n  moderator {\n    id\n    username\n    __typename\n  }\n  approvalDate\n  deletedAt\n  createdAt\n  updatedAt\n  mayBePublished\n  prevFeeMultiplier\n  sellerNotifiedAboutFeeChange\n  __typename\n}\n\nfragment ItemFields on Item {\n  id\n  slug\n  name\n  description\n  rawPrice\n  price\n  attributes\n  status\n  priorityPosition\n  sellerType\n  feeMultiplier\n  user {\n    ...ItemUser\n    __typename\n  }\n  buyer {\n    ...ItemUser\n    __typename\n  }\n  attachments {\n    ...PartialFile\n    __typename\n  }\n  category {\n    ...RegularGameCategory\n    __typename\n  }\n  game {\n    ...RegularGameProfile\n    __typename\n  }\n  comment\n  dataFields {\n    ...GameCategoryDataFieldWithValue\n    __typename\n  }\n  obtainingType {\n    ...GameCategoryObtainingType\n    __typename\n  }\n  __typename\n}\n\nfragment ItemUser on UserFragment {\n  ...UserEdgeNode\n  __typename\n}\n\nfragment UserEdgeNode on UserFragment {\n  ...RegularUserFragment\n  __typename\n}\n\nfragment RegularUserFragment on UserFragment {\n  id\n  username\n  role\n  avatarURL\n  isOnline\n  isBlocked\n  rating\n  testimonialCounter\n  createdAt\n  supportChatId\n  systemChatId\n  __typename\n}\n\nfragment PartialFile on File {\n  id\n  url\n  __typename\n}\n\nfragment RegularGameCategory on GameCategory {\n  id\n  slug\n  name\n  categoryId\n  gameId\n  obtaining\n  options {\n    ...RegularGameCategoryOption\n    __typename\n  }\n  props {\n    ...GameCategoryProps\n    __typename\n  }\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  useCustomObtaining\n  autoConfirmPeriod\n  autoModerationMode\n  agreements {\n    ...RegularGameCategoryAgreement\n    __typename\n  }\n  feeMultiplier\n  __typename\n}\n\nfragment RegularGameCategoryOption on GameCategoryOption {\n  id\n  group\n  label\n  type\n  field\n  value\n  valueRangeLimit {\n    min\n    max\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryProps on GameCategoryPropsObjectType {\n  minTestimonials\n  minTestimonialsForSeller\n  __typename\n}\n\nfragment RegularGameCategoryAgreement on GameCategoryAgreement {\n  description\n  gameCategoryId\n  gameCategoryObtainingTypeId\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment RegularGameProfile on GameProfile {\n  id\n  name\n  type\n  slug\n  logo {\n    ...PartialFile\n    __typename\n  }\n  __typename\n}\n\nfragment GameCategoryDataFieldWithValue on GameCategoryDataFieldWithValue {\n  id\n  label\n  type\n  inputType\n  copyable\n  hidden\n  required\n  value\n  __typename\n}\n\nfragment GameCategoryObtainingType on GameCategoryObtainingType {\n  id\n  name\n  description\n  gameCategoryId\n  noCommentFromBuyer\n  instructionForBuyer\n  instructionForSeller\n  sequence\n  feeMultiplier\n  agreements {\n    ...MinimalGameCategoryAgreement\n    __typename\n  }\n  props {\n    minTestimonialsForSeller\n    __typename\n  }\n  __typename\n}\n\nfragment MinimalGameCategoryAgreement on GameCategoryAgreement {\n  description\n  iconType\n  id\n  sequence\n  __typename\n}\n\nfragment StatusPaymentTransaction on Transaction {\n  id\n  operation\n  direction\n  providerId\n  status\n  statusDescription\n  statusExpirationDate\n  value\n  props {\n    paymentURL\n    __typename\n  }\n  __typename\n}\n\nfragment RegularForeignItem on ForeignItem {\n  ...ItemFields\n  __typename\n}"
        }
        try:
            response = tls_requests.post(self.api_url, headers=globalheaders, cookies=self.cookies, json=json_data)
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
        slug = link.replace("https://playerok.com/products", "").split('?')[0].strip('/')
        params = {
            "operationName": "item",
            "variables": f'{{"slug":"{slug}"}}',
            "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"937add98f8a20b9ff4991bc6ba2413283664e25e7865c74528ac21c7dff86e24"}}'
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
        response = tls_requests.get(self.api_url, params=params, cookies=self.cookies, headers=globalheaders)
        data = response.json()
        sequence = data['data']['item']['sequence']
        return sequence