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
        action = Action()
        action.message_id = message_id
        action.text = action_text
        self.logger.debug(f"Adding action to message_id {action.message_id} with textlen {len(action_text)}")
        self.session.add(action)
        self.session.commit()
        return action
