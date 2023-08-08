from app.services.player_health_service import PlayerHealthService

class FunctionCallDTO
    def __init__(self, name: String, arguments):
        self.name = name

class FeedbackFunctionExecutionService:
    def __init__(self):
        self.feedback_functions = {
            "update_player_health": self.player_health_service.
        }
        self.player_health_service = PlayerHealthService.update_player_health()
        self.functions = [
            {
                "name": "update_player_health",
                "description": "Update player health value when Situation or Decision leads to it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "delta": {
                            "type": "int",
                            "description": "Amount of change. Will be negative for a health loss.",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Sentence that describes what have happened. For example: \"Lost some health due to a fight with yourself.\"",
                        },
                        "impact": {
                            "type": "string",
                            "description": "Sentence that describes the impact of the event on Player's body. For example: \"Bruises\", \"Headache\", \"Traumatising experience\".",
                        },
                    },
                    "required": ["delta", "reason", "impact"],
                },
            }
        ]

    def execute(self, function_call):
        # Record the health update event
        event = Event(user_id=user_id, delta=delta, reason=reason, impact=impact)
        self.session.add(event)

        # Update the player's health
        user = self.session.query(User).filter(User.id == user_id).one()
        user.health += delta

        self.session.commit()
