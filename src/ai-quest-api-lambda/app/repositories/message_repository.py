from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.logger import configure_logger
from app.config.mysql import configure_mysql
from app.models.message import Message
from uuid import UUID


class MessageRepository:
    def __init__(self):
        engine = configure_mysql()
        self.session = Session(engine)
        self.logger = configure_logger()

    def get_messages_by_user_id(self, user_id: UUID):
        sql = text("SELECT * FROM messages WHERE user_id = UUID_TO_BIN(:user_id) ORDER BY timestamp DESC")
        result = self.session.execute(sql, {'user_id': user_id.hex})
        messages = result.fetchall()

        self.logger.debug(f"Retrieved {len(messages)} messages for user_id {user_id}")
        return messages

    def add_message(self, message: Message):
        self.logger.debug(f"Adding message {message.id} for user_id {message.user_id}")
        self.session.add(message)
        self.session.commit()
