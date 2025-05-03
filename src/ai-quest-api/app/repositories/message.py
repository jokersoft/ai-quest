from app.entities.message import Message


class MessageRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def add(self, message: Message):
        self.db_session.add(message)
        self.db_session.commit()
        return message.id

    def get_message(self, message_id: str) -> Message:
        return self.db_session.query(Message).filter(Message.id == message_id).first()
