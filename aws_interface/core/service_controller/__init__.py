from .base import ServiceController
from .bill import BillServiceController
from .auth import AuthServiceController
from .database import DatabaseServiceController
from .storage import StorageServiceController


sc_list = [
    BillServiceController, AuthServiceController, DatabaseServiceController, StorageServiceController
]
sc_dict = dict([(sc.RECIPE, sc) for sc in sc_list])
