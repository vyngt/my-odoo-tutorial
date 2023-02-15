import requests
import json
import random
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
_handler = logging.StreamHandler()
_logger.addHandler(_handler)


def gen_number():
    return random.randint(0, 1000000000)


class AuthException(BaseException):
    pass


class ResponseException(BaseException):
    pass


class BaseAPI:
    model = None

    def __init__(self, url: str, database: str) -> None:
        self.url = url
        self.database = database
        self.uid: int | None = None
        self.access_pw: str | None = None

    def _json_rpc(self, method, params):
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": gen_number(),
        }

        _logger.debug(f"_json_rpc:data: {data}")

        response = requests.post(
            self.url, json=data, headers={"Content-Type": "application/json"}
        )

        _logger.debug(f"_json_rpc:response: {response.content}")

        data = json.loads(response.content)
        if "result" not in data:
            raise ResponseException(f"Response: {data['error']}")

        return data["result"]

    def _call(self, service: str, method: str, *args):
        return self._json_rpc(
            "call",
            {"service": service, "method": method, "args": args},
        )

    def call(self, service: str, method: str, *args):
        if self.uid is None:
            raise AuthException("Are you login?")

        if self.model is not None:
            return self._call(
                service,
                method,
                *((self.database, self.uid, self.access_pw, self.model) + args),
            )

        return self._call(
            service, method, *((self.database, self.uid, self.access_pw) + args)
        )

    def execute_kw(self, *args):
        return self.call("object", "execute_kw", *args)

    def login(self, user: str, password: str):
        """
        params:
            :user: str, username

            :password: str, password or api key
        """
        try:
            uid = self._call("common", "login", self.database, user, password)
        except ResponseException:
            raise AuthException("Login Failed")

        self.access_pw = password
        self.uid = uid
        return True


class TutorialAPI(BaseAPI):
    model = "tutorial.library.book"


# Change here
PROTOCOL = "http"
HOST = "localhost"  # <-
PORT = "8069"  # <-

BASE_URL = f"{PROTOCOL}://{HOST}:{PORT}"
JSONRPC_URL = f"{BASE_URL}/jsonrpc"


DB = ""  # <- your database name>
USER = ""  # <- your username in database
API_KEY = ""  # <- password or api key

api = TutorialAPI(JSONRPC_URL, DB)
api.login(USER, API_KEY)

## tutorial.library.book

## Search
api.execute_kw("search", [[["is_available", "=", True]]])

## Search Count
api.execute_kw("search_count", [[["active", "=", True]]])

## Read
api.execute_kw("read", [1], {"fields": ["name"]})

## Get fields
api.execute_kw("fields_get", [], {"attributes": ["string", "help", "type"]})

## Search and Read
api.execute_kw(
    "search_read",
    [[["name", "ilike", "rpc"]]],
    {"fields": ["name"], "limit": 5, "offset": 6},
)

## Create
api.execute_kw("create", [{"name": f"RPC {gen_number()}"}])

## Update
# get last record
_id = api.execute_kw("search", [[]])[-1]

api.execute_kw("write", [[_id], {"name": "Changed from RPC"}])

## Name Get
api.execute_kw("name_get", [1])

## Delete
api.execute_kw("unlink", [[_id]])
