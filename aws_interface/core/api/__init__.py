from .base import API
from .bill import BillAPI
from .auth import AuthAPI
from .database import DatabaseAPI
from .storage import StorageAPI
from .logic import LogicAPI

api_list = [
    BillAPI,
    AuthAPI,
    DatabaseAPI,
    StorageAPI,
    LogicAPI
]
api_dict = dict([(api.get_recipe(), api) for api in api_list])
