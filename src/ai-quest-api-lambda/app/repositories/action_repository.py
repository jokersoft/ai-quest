from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.logger import configure_logger
from app.models.action import Action


class ActionRepository:
    def __init__(self, db_session: Session):
        self.session = db_session
        self.logger = configure_logger()

    def get(self, message_id: str):
        sql = text("SELECT * FROM actions WHERE message_id = :message_id")
        result = self.session.execute(sql, {'message_id': message_id})
        actions = result.fetchall()
        self.logger.debug(f"Retrieved {len(actions)} actions for message_id {message_id}")
        return actions

    def add(self, message_id: str, action_text: str):
        action = Action(message_id=message_id, text=action_text)
        self.session.add(action)
        self.session.commit()
        return action

    def add_all(self, message_id: str, action_texts: list):
        actions = []
        for action_text in action_texts:
            actions.append(Action(message_id=message_id, text=action_text))

        self.session.add_all(actions)
        self.session.commit()
        return actions
