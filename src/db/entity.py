from datetime import datetime
from typing import Optional

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.postgres import Base


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)
    load_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    subscriptions: Mapped[list['Subscription']] = relationship(
        'Subscription', back_populates='user'
    )


class Server(Base):
    __tablename__ = 'servers'

    server_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    login: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(255), nullable=False)
    server_available_load: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    query_params: Mapped[str] = mapped_column(String(255), nullable=False)
    server_ip: Mapped[str] = mapped_column(String(255), nullable=False)

    subscriptions: Mapped[list['Subscription']] = relationship(
        'Subscription', back_populates='server'
    )


class Subscription(Base):
    __tablename__ = 'subscriptions'

    sub_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.user_id'), nullable=False
    )
    server_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('servers.server_id'), nullable=False
    )
    user_uuid: Mapped[str] = mapped_column(String(255), nullable=False)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    end_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped['User'] = relationship('User', back_populates='subscriptions')
    server: Mapped['Server'] = relationship('Server', back_populates='subscriptions')
