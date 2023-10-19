from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SpyOffsets(Base):  # type: ignore
    __tablename__ = "spy_offsets"

    username = Column(String(1024), primary_key=True)
    last_offset = Column(BigInteger, nullable=False)
    crawl_link = Column(Boolean, default=False)
    room_name = Column(String(1024))
    link = Column(String(1024))


class Message(Base):  # type: ignore
    __tablename__ = "message"

    offset = Column(BigInteger, nullable=False)
    username = Column(String(1024), nullable=False)
    sender_id = Column(BigInteger, nullable=False)
    content = Column(Text)
    send_time = Column(DateTime)
    id = Column(BigInteger, primary_key=True)

    __table_args__ = (
        UniqueConstraint("offset", "username", name="messages_offset_username_key"),
    )
