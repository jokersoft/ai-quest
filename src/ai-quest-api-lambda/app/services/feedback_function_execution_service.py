import json
from app.config.logger import configure_logger
from app.services.player_health_service import PlayerHealthService

class FeedbackFunctionExecutionService:
    def __init__(self):
        self.player_health_service = PlayerHealthService()
        with open('./app/data/multi_function_call.json', 'r') as file:
            self.functions = file.read().strip()

        self.available_functions = []
        for function in self.functions:
            if function['name'] == 'multi_function':
                self.available_functions.extend(function['parameters']['properties'].keys())
        self.logger = configure_logger()

    def execute(self, function_name, arguments):
        for available_function_name in self.available_functions:
            if function_name == available_function_name:
                function_name(**arguments)

        raise ValueError(f"No function found for name: {function_call.name}")
