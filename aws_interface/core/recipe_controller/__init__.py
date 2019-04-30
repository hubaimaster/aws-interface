from .base import RecipeController

from .bill import BillRecipeController
from .auth import AuthRecipeController
from .database import DatabaseRecipeController
from .storage import StorageRecipeController
from .logic import LogicRecipeController
from .log import LogRecipeController

rc_list = [
    BillRecipeController,
    AuthRecipeController,
    DatabaseRecipeController,
    StorageRecipeController,
    LogicRecipeController,
    LogRecipeController,
]
recipe_list = [rc.RECIPE for rc in rc_list]
rc_dict = dict([(rc.RECIPE, rc) for rc in rc_list])
