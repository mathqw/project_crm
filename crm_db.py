from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import asyncio


DATABASE_URL = "postgresql+asyncpg://postgres:mat1410vey@localhost:5432/crm_db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with async_session() as db:
        yield db

class User(Base):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="manager"   # admin / rop / manager
    )

    clients = relationship("Client", back_populates="manager")
    deals = relationship("Deal", back_populates="manager")

class Client(Base):
    __tablename__ = "Client"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)

    country: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    street: Mapped[str] = mapped_column(String(100), nullable=False)

    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    website: Mapped[str] = mapped_column(String(100))

    manager_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("User.id"), nullable=False
    )

    manager = relationship("User", back_populates="clients")
    deals = relationship("Deal", back_populates="client")


class Deal(Base):
    __tablename__ = "Deal"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="UAH", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Client.id"), nullable=False
    )
    manager_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("U ser.id"), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="new"  # new / in_progress / closed
    )

    client = relationship("Client", back_populates="deals")
    manager = relationship("User", back_populates="deals")

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
