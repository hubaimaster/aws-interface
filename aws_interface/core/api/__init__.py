from .base import API
from .bill import BillAPI
from .auth import AuthAPI
from .database import DatabaseAPI
from .storage import StorageAPI
from .logic import LogicAPI
from .log import LogAPI

api_list = [
    BillAPI,
    AuthAPI,
    DatabaseAPI,
    StorageAPI,
    LogicAPI,
    LogAPI,
]
