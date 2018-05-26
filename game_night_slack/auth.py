from requests.auth import AuthBase

class GameNightAuth(AuthBase):

    def __call__(self, request):
        request.headers['Authorization'] = 'Bearer ' + self.key
        return request

    def __init__(self, key):
        self.key = key
