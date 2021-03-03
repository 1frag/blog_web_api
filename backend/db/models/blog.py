import enum

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg_sa

from sqlalchemy.ext.declarative import declarative_base

from core.config import settings

engine = sa.create_engine(settings.database_url)


class Base(declarative_base(bind=engine)):
    __abstract__ = True
    __table__: sa.Table


user_id_seq = sa.Sequence("app_users_id_seq")
message_id_seq = sa.Sequence("app_messages_id_seq")
attachment_id_seq = sa.Sequence("app_attachments_id_seq")
like_id_seq = sa.Sequence("app_likes_id_seq")


class User(Base):
    __tablename__ = "app_users"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False,
                   server_default=user_id_seq.next_value())
    login = sa.Column(sa.String(63), unique=True)
    password = sa.Column(sa.String(127))


class Message(Base):
    __tablename__ = "app_messages"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False,
                   server_default=message_id_seq.next_value())
    title = sa.Column(sa.String(255))
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    author = sa.Column(sa.Integer, sa.ForeignKey('app_users.id', ondelete="CASCADE"),
                       nullable=False)
    user = sa.orm.relationship('app_users', foreign_keys=[author])


class AttachmentKind(enum.Enum):
    text = 1
    media = 2
    link = 3


class Attachment(Base):
    __tablename__ = "app_attachments"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False,
                   server_default=attachment_id_seq.next_value())
    kind = sa.Column(sa.Enum(AttachmentKind))
    data = sa.Column(pg_sa.TEXT)

    message_id = sa.Column(sa.Integer, sa.ForeignKey(
        'app_messages.id', ondelete="CASCADE"), nullable=False)
    message = sa.orm.relationship('app_messages', foreign_keys=[message_id])


class Like(Base):
    __tablename__ = "app_likes"
    __table_args__ = sa.UniqueConstraint('user_id', 'message_id'),

    id = sa.Column(sa.Integer, primary_key=True, nullable=False,
                   server_default=like_id_seq.next_value())

    user_id = sa.Column(sa.Integer, sa.ForeignKey('app_users.id', ondelete="CASCADE"),
                        nullable=False)
    user = sa.orm.relationship('app_users', foreign_keys=[user_id])

    message_id = sa.Column(sa.Integer, sa.ForeignKey(
        'app_messages.id', ondelete="CASCADE"), nullable=False)
    message = sa.orm.relationship('app_messages', foreign_keys=[message_id])


users = User.__table__
messages = Message.__table__
attachments = Attachment.__table__
likes = Like.__table__
