import os
import json
from app.config.logger import configure_logger
from app.services.player_health_service import PlayerHealthService


class FeedbackFunctionExecutionService:
    def __init__(self):
        self.player_health_service = PlayerHealthService()
        with open('./app/data/multi_function_call.json', 'r') as file:
            self.functions = json.load(file)

        self.available_functions = ['multi_function']
        for function in self.functions:
            if function['name'] == 'multi_function':
                self.available_functions.extend(function['parameters']['properties'].keys())
        self.logger = configure_logger()

    def execute(self, function_name, arguments):
        for available_function_name in self.available_functions:
            if function_name == 'multi_function':
                self.logger.debug(f"multi_function called with: {json.dumps(arguments)}")
                # TODO: foreach keys() call sub_functions with self.execute()
            if function_name == 'update_player_health':
                self.logger.debug(f"update_player_health called with: {json.dumps(arguments)}")
                # TODO: current_user_provider, actual calls
                # self.player_health_service.update_player_health(user_id, arguments.delta, arguments.reason, arguments.impact)
            if function_name == 'update_player_inventory':
                self.logger.debug(f"update_player_inventory called with: {json.dumps(arguments)}")
                # TODO

        raise ValueError(f"No function found for name: {function_name}")

    @staticmethod
    def is_enabled() -> bool:
        return int(os.environ["FUNCTION_CALL_ENABLED"]) == 1
