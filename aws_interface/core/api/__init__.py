from .base import API
from .bill import BillAPI
from .auth import AuthAPI
from .database import DatabaseAPI
from .storage import StorageAPI
from .sdk import generate_sdk


api_list = [
    BillAPI, AuthAPI, DatabaseAPI, StorageAPI
]
api_dict = dict([(api.get_recipe(), api) for api in api_list])
