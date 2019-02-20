from .base import RecipeController

from .bill import BillRecipeController
from .auth import AuthRecipeController
from .database import DatabaseRecipeController
from .storage import StorageRecipeController

rc_list = [
    BillRecipeController, AuthRecipeController, DatabaseRecipeController, StorageRecipeController
]
recipes = [rc.RECIPE_TYPE for rc in rc_list]
rc_dict = dict([(rc.RECIPE_TYPE, rc) for rc in rc_list])
