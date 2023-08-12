import requests
from bs4 import BeautifulSoup
from skyeng_database import SkyengDatabase

LOGIN_URL = "https://id.skyeng.ru/login"
LOGIN_SUBMIT_URL = "https://id.skyeng.ru/frame/login-submit"
JWT_URL = "https://id.skyeng.ru/user-api/v1/auth/jwt"
WORD_SETS_URL = "https://api.words.skyeng.ru/api/for-vimbox/v1/wordsets.json"
WORDS_FROM_SET_URL = "https://api.words.skyeng.ru/api/v1/wordsets/{set_id}/words.json"
WORDS_DATA_URL = "https://dictionary.skyeng.ru/api/for-services/v2/meanings"


class SkyengUser:
    def __init__(self, user_id, database: SkyengDatabase):
        self.user_id = user_id
        self.db = database
        self.client = requests.Session()

    def get_token_from_db(self):
        return self.db.get_token(self.user_id)

    def get_csrf(self):
        response = self.client.get(LOGIN_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfToken'})['value']
        return csrf_token

    def get_jwt(self):
        response = self.client.post(JWT_URL)
        return next(iter(response.cookies.values()), None)

    def success_response(self, message, **kwargs):
        return {"status": "ok", "message": message, **kwargs}

    def error_response(self, message, details=None):
        return {"status": "error", "message": message, "details": details}

    def login(self, username: str = None, password: str = None):
        token = self.get_token_from_db()
        if token:
            return self.success_response("Already logged in", token=token)
        try:
            csrf_token = self.get_csrf()
            login_data = {
                "username": username,
                "password": password,
                "csrfToken": csrf_token
            }
            response = self.client.post(LOGIN_SUBMIT_URL, data=login_data)
            if response.status_code != 200:
                return self.error_response("Login failed", response.text)
            token = self.get_jwt()
            self.db.insert_token(self.user_id, token)
            return self.success_response("Data received", token=token)
        except Exception as e:
            return self.error_response("An exception occurred during login", str(e))

    def get_word_sets(self, page_number, page_size):
        token = self.get_token_from_db()
        if not token:
            return self.error_response("Not logged in")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {
                "page": page_number,
                "pageSize": page_size
            }
            response = self.client.get(WORD_SETS_URL, headers=headers, params=params)
            if response.status_code != 200:
                return self.error_response("Failed to fetch word sets", response.text)
            word_sets = response.json()['data']
            for word_set in word_sets:
                word_set.pop('images', None)
                word_set.pop('progress', None)
                word_set.pop('subtitle', None)
                word_set.pop('sourceSet', None)
            return self.success_response("Word sets fetched successfully", sets=word_sets, page=page_number,
                                          pageSize=page_size, lastPage=response.json()['meta']['lastPage'])
        except Exception as e:
            return self.error_response("An exception occurred while fetching word sets", str(e))

    def get_words_from_set(self, set_id):
        token = self.get_token_from_db()
        if not token:
            return self.error_response("Not logged in")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.client.get(WORDS_FROM_SET_URL.format(set_id=set_id), headers=headers)
            if response.status_code != 200:
                return self.error_response("Failed to fetch words from set", response.text)
            return self.success_response("Words fetched successfully", words=response.json()['data'])
        except Exception as e:
            return self.error_response("An exception occurred while fetching words from set", str(e))

    def get_words_data(self, word_ids):
        token = self.get_token_from_db()
        if not token:
            return self.error_response("Not logged in")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"ids": ",".join(map(str, word_ids))}
            response = self.client.get(WORDS_DATA_URL, headers=headers, params=params)
            if response.status_code != 200:
                return self.error_response("Failed to fetch words data", response.text)
            words = response.json()
            for word in words:
                word.pop('soundUrl', None)
                word.pop('images', None)
                word.pop('transcription', None)
                word.pop('examples', None)
                for key, value in word.items():
                    if isinstance(value, dict):
                        value.pop('soundUrl', None)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                item.pop('soundUrl', None)
            return self.success_response("Words data fetched successfully", Words_data=words)
        except Exception as e:
            return self.error_response("An exception occurred while fetching words data", str(e))
