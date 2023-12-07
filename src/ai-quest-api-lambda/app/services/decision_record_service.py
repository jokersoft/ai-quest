from sqlalchemy.orm import Session
from app.config.logger import configure_logger
from app.config.mysql import configure_mysql
from app.models.user import User


class DecisionRecordService:
    def __init__(self):
        engine = configure_mysql()
        self.session = Session(engine)
        self.logger = configure_logger()

    def record_decision(self, description):
        self.logger.debug(f"Recording decision record: {description}")
        # Record the Decision
        # event = Event(user_id=user_id, delta=delta, reason=reason, impact=impact)
        # self.session.add(event)

        # Update the player's health
        # user = self.session.query(User).filter(User.id == user_id).one()
        # user.health += delta

        # self.session.commit()
