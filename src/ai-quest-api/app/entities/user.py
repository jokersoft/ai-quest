from sqlalchemy import BINARY, Boolean, Column, Index, String
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    email = Column(String(254), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)

    def get_id(self) -> uuid.UUID:
        """Returns the UUID of the user."""
        if not self.id:
            raise ValueError("User ID is not set.")
        return uuid.UUID(bytes=self.id)

    __table_args__ = (
        Index('idx_email', 'email'),
    )
