from sqlalchemy.orm import Session
from app.config.mysql import configure_mysql
from app.models.message import Message
from uuid import UUID

class MessageRepository:
    def __init__(self):
        engine = configure_mysql()
        self.session = Session(engine)

    def get_messages_by_user_id(self, user_id: UUID):
        return self.session.query(Message).filter(Message.user_id == user_id.bytes).order_by(Message.timestamp.desc()).all()

    def add_message(self, message: Message):
        self.session.add(message)
        self.session.commit()
