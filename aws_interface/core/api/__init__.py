from .base import API
from .bill import BillAPI
from .auth import AuthAPI
from .database import DatabaseAPI
from .storage import StorageAPI
from .logic import LogicAPI
from .log import LogAPI
from .schedule import ScheduleAPI
from .notification import NotificationAPI

api_list = [
    BillAPI,
    AuthAPI,
    DatabaseAPI,
    StorageAPI,
    LogicAPI,
    LogAPI,
    ScheduleAPI,
    NotificationAPI,
]
