from .base import ServiceController
from .bill import BillServiceController
from .auth import AuthServiceController
from .database import DatabaseServiceController
from .storage import StorageServiceController
from .logic import LogicServiceController
from .log import LogServiceController


sc_list = [
    BillServiceController,
    AuthServiceController,
    DatabaseServiceController,
    StorageServiceController,
    LogicServiceController,
    LogServiceController,
]
sc_dict = dict([(sc.SERVICE_TYPE, sc) for sc in sc_list])
