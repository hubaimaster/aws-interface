from .base import ServiceController
from .bill import BillServiceController
from .auth import AuthServiceController
from .database import DatabaseServiceController
from .storage import StorageServiceController
from .logic import LogicServiceController
from .log import LogServiceController


SC_LIST = [
    BillServiceController,
    AuthServiceController,
    DatabaseServiceController,
    StorageServiceController,
    LogicServiceController,
    LogServiceController,
]
SC_DICT = {sc.SERVICE_TYPE: sc for sc in SC_LIST}
