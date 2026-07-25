from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    next_payday: Mapped[date | None] = mapped_column(Date, nullable=True)
    payday_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    payday_wallet_id: Mapped[int | None] = mapped_column(ForeignKey("wallets.id"), nullable=True)
    payday_category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payday_note: Mapped[str | None] = mapped_column(String(140), nullable=True)
    totp_secret: Mapped[str | None] = mapped_column(String(32), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    wallets: Mapped[list["Wallet"]] = relationship(
        back_populates="owner", foreign_keys="Wallet.user_id", cascade="all, delete-orphan"
    )
    obligations: Mapped[list["FixedObligation"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    wallet_adjustments: Mapped[list["WalletAdjustment"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    incomes: Mapped[list["Income"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    kind: Mapped[str] = mapped_column(String(20))  # ewallet | digital_bank | bank | cash
    label: Mapped[str] = mapped_column(String(50))
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    owner: Mapped["User"] = relationship(back_populates="wallets", foreign_keys=[user_id])


class WalletAdjustment(Base):
    __tablename__ = "wallet_adjustments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"))
    wallet_label: Mapped[str] = mapped_column(String(50))
    delta: Mapped[float] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    owner: Mapped["User"] = relationship(back_populates="wallet_adjustments")


class Income(Base):
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"))
    wallet_label: Mapped[str] = mapped_column(String(50))
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(String(20))  # see INCOME_CATEGORY_PATTERN in schemas.py
    note: Mapped[str | None] = mapped_column(String(140), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    owner: Mapped["User"] = relationship(back_populates="incomes")


class FixedObligation(Base):
    __tablename__ = "fixed_obligations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    label: Mapped[str] = mapped_column(String(80))
    amount: Mapped[float] = mapped_column(Numeric(12, 2))

    owner: Mapped["User"] = relationship(back_populates="obligations")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    wallet_id: Mapped[int | None] = mapped_column(ForeignKey("wallets.id"), nullable=True)
    wallet_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(String(20))  # see CATEGORY_PATTERN in schemas.py
    note: Mapped[str | None] = mapped_column(String(140), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    owner: Mapped["User"] = relationship(back_populates="expenses")
