from .base import API
from core import sdk


def generate_sdk(apis, platform):
    controller_pairs = []
    api: API
    for api in apis:
        rc = api.get_recipe_controller()
        sc = api.service_controller
        controller_pairs.append((rc, sc))
    return sdk.generate(controller_pairs, platform)
