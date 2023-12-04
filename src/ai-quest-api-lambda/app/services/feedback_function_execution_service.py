import os
import json
from app.config.logger import configure_logger
from app.services.decision_record_service import DecisionRecordService
from app.services.player_health_service import PlayerHealthService


class FeedbackFunctionExecutionService:
    def __init__(self):
        self.decision_record_service = DecisionRecordService()
        self.logger = configure_logger()

    def execute(self, function_name, arguments):
        if function_name == 'record_decision':
            self.logger.debug(f"record_decision called with: {json.dumps(arguments)}")
            return 'record_decision executed'

        raise ValueError(f"No function found for name: {function_name}")

    @staticmethod
    def is_enabled() -> bool:
        return int(os.environ["FUNCTION_CALL_ENABLED"]) == 1
