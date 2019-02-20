from abc import ABCMeta


class API(metaclass=ABCMeta):
    """
    Make sure to set RC_CLASS and SC_CLASS when you inherit this class.
    """
    RC_CLASS = None
    SC_CLASS = None

    def __init__(self, bundle, app_id, recipe_json_string=None):
        """
        :param bundle:
        :param app_id:
        :param recipe_json_string:
        """
        self.bundle = bundle
        self.app_id = app_id
        self.recipe_json_string = recipe_json_string

        self.recipe_controller = type(self).RC_CLASS()
        self.service_controller = type(self).SC_CLASS(bundle, app_id)

        if self.recipe_json_string:
            self.recipe_controller.load_json_string(self.recipe_json_string)

    def apply(self):
        self.service_controller.apply(self.recipe_controller)

    def set_recipe_controller(self, recipe_controller):
        self.recipe_controller = recipe_controller

    def get_recipe_controller(self):
        return self.recipe_controller

    def get_recipe_json_string(self):
        return self.get_recipe_controller().to_json()

    def get_rest_api_url(self):
        return self.service_controller.get_rest_api_url(self.recipe_controller)

    @classmethod
    def get_recipe(cls):
        return cls.RC_CLASS.RECIPE
