import base64
import io
from datetime import date, datetime, timezone
from decimal import Decimal

import pyotp
import qrcode
import qrcode.image.svg
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import delete, inspect, select, text, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_mfa_challenge_token,
    decode_mfa_challenge_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import Base, engine, get_db
from app.models import Expense, Income, User, Wallet, WalletAdjustment
from app.schemas import (
    ChangePasswordRequest,
    DashboardOut,
    ExpenseCreate,
    ExpenseOut,
    ExpenseUpdate,
    IncomeCreate,
    IncomeOut,
    IncomeUpdate,
    LoginOut,
    MfaLoginRequest,
    PaydayUpdate,
    Token,
    TwoFactorDisableRequest,
    TwoFactorSetupOut,
    TwoFactorVerifyRequest,
    UserCreate,
    UserOut,
    WalletAdjustmentOut,
    WalletCreate,
    WalletOut,
    WalletUpdate,
)

Base.metadata.create_all(bind=engine)


def _ensure_columns():
    """create_all only creates missing tables, not missing columns on existing ones."""
    expected = {
        "users": {
            "next_payday": "DATE",
            "payday_amount": "NUMERIC(12, 2)",
            "payday_wallet_id": "INTEGER",
            "payday_category": "VARCHAR(20)",
            "payday_note": "VARCHAR(140)",
            "totp_secret": "VARCHAR(32)",
            "totp_enabled": "BOOLEAN DEFAULT 0",
        },
        "expenses": {
            "wallet_id": "INTEGER",
            "wallet_label": "VARCHAR(50)",
        },
    }
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        for table, columns in expected.items():
            if table not in tables:
                continue
            existing = {col["name"] for col in inspector.get_columns(table)}
            for name, sql_type in columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {sql_type}"))


def _ensure_nullable_wallet_refs():
    """wallet_id on incomes/wallet_adjustments used to be NOT NULL; relax it so
    deleting a wallet with history doesn't violate the FK constraint."""
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE incomes ALTER COLUMN wallet_id DROP NOT NULL"))
        conn.execute(text("ALTER TABLE wallet_adjustments ALTER COLUMN wallet_id DROP NOT NULL"))


_ensure_columns()
_ensure_nullable_wallet_refs()

app = FastAPI(title="Safe-to-Spend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# auth
# ---------------------------------------------------------------------------
@app.post("/api/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/api/auth/login", response_model=LoginOut)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form_data.username))
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    if user.totp_enabled:
        return LoginOut(requires_2fa=True, mfa_token=create_mfa_challenge_token(subject=str(user.id)))

    return LoginOut(access_token=create_access_token(subject=str(user.id)))


@app.post("/api/auth/login/2fa", response_model=Token)
def login_2fa(payload: MfaLoginRequest, db: Session = Depends(get_db)):
    user_id = decode_mfa_challenge_token(payload.mfa_token)
    user = db.get(User, int(user_id))
    if not user or not user.totp_enabled or not user.totp_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired 2FA challenge")

    if not pyotp.TOTP(user.totp_secret).verify(payload.code, valid_window=1):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect code")

    return Token(access_token=create_access_token(subject=str(user.id)))


@app.post("/api/auth/change-password", response_model=UserOut)
def change_password(
    payload: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    db.refresh(current_user)
    return current_user


@app.post("/api/auth/2fa/setup", response_model=TwoFactorSetupOut)
def setup_2fa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    secret = pyotp.random_base32()
    current_user.totp_secret = secret
    current_user.totp_enabled = False
    db.commit()

    uri = pyotp.TOTP(secret).provisioning_uri(name=current_user.email, issuer_name="Safe-to-Spend")

    qr_img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    qr_img.save(buf)
    qr_data_uri = f"data:image/svg+xml;base64,{base64.b64encode(buf.getvalue()).decode()}"

    return TwoFactorSetupOut(secret=secret, otpauth_uri=uri, qr_code_data_uri=qr_data_uri)


@app.post("/api/auth/2fa/verify", response_model=UserOut)
def verify_2fa(
    payload: TwoFactorVerifyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not current_user.totp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start 2FA setup first")

    if not pyotp.TOTP(current_user.totp_secret).verify(payload.code, valid_window=1):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect code")

    current_user.totp_enabled = True
    db.commit()
    db.refresh(current_user)
    return current_user


@app.post("/api/auth/2fa/disable", response_model=UserOut)
def disable_2fa(
    payload: TwoFactorDisableRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    current_user.totp_secret = None
    current_user.totp_enabled = False
    db.commit()
    db.refresh(current_user)
    return current_user


@app.get("/api/auth/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


# ---------------------------------------------------------------------------
# payday
# ---------------------------------------------------------------------------
@app.put("/api/payday", response_model=UserOut)
def set_payday(payload: PaydayUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updates = payload.model_dump(exclude_unset=True)

    if "wallet_id" in updates and updates["wallet_id"] is not None:
        _get_owned_wallet(updates["wallet_id"], current_user, db)

    if "next_payday" in updates:
        current_user.next_payday = updates["next_payday"]
    if "amount" in updates:
        current_user.payday_amount = updates["amount"]
    if "wallet_id" in updates:
        current_user.payday_wallet_id = updates["wallet_id"]
    if "category" in updates:
        current_user.payday_category = updates["category"]
    if "note" in updates:
        current_user.payday_note = updates["note"]

    db.commit()
    db.refresh(current_user)
    return current_user


# ---------------------------------------------------------------------------
# wallets
# ---------------------------------------------------------------------------
@app.get("/api/wallets", response_model=list[WalletOut])
def list_wallets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Wallet).where(Wallet.user_id == current_user.id)).all()


@app.post("/api/wallets", response_model=WalletOut, status_code=status.HTTP_201_CREATED)
def create_wallet(payload: WalletCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = Wallet(user_id=current_user.id, **payload.model_dump())
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def _get_owned_wallet(wallet_id: int, current_user: User, db: Session, for_update: bool = False) -> Wallet:
    wallet = db.get(Wallet, wallet_id, with_for_update=for_update)
    if not wallet or wallet.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return wallet


@app.patch("/api/wallets/{wallet_id}", response_model=WalletOut)
def update_wallet(
    wallet_id: int,
    payload: WalletUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = _get_owned_wallet(wallet_id, current_user, db, for_update=True)
    updates = payload.model_dump(exclude_unset=True)

    if "balance" in updates:
        delta = Decimal(str(updates["balance"])) - Decimal(str(wallet.balance))
        if delta != 0:
            db.add(
                WalletAdjustment(
                    user_id=current_user.id,
                    wallet_id=wallet.id,
                    wallet_label=wallet.label,
                    delta=delta,
                )
            )

    for field, value in updates.items():
        setattr(wallet, field, value)
    db.commit()
    db.refresh(wallet)
    return wallet


@app.delete("/api/wallets/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wallet(wallet_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = _get_owned_wallet(wallet_id, current_user, db)

    db.execute(delete(Expense).where(Expense.wallet_id == wallet.id))
    db.execute(delete(Income).where(Income.wallet_id == wallet.id))
    db.execute(delete(WalletAdjustment).where(WalletAdjustment.wallet_id == wallet.id))
    if current_user.payday_wallet_id == wallet.id:
        current_user.payday_wallet_id = None

    db.delete(wallet)
    db.commit()


@app.get("/api/wallets/adjustments", response_model=list[WalletAdjustmentOut])
def list_wallet_adjustments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = (
        select(WalletAdjustment)
        .where(WalletAdjustment.user_id == current_user.id)
        .order_by(WalletAdjustment.created_at.desc())
    )
    return db.scalars(stmt).all()


# ---------------------------------------------------------------------------
# income (salary, interest, investment, cashback, allowance, bonus, other)
# ---------------------------------------------------------------------------
@app.get("/api/income", response_model=list[IncomeOut])
def list_income(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Income).where(Income.user_id == current_user.id).order_by(Income.created_at.desc())
    return db.scalars(stmt).all()


@app.post("/api/income", response_model=IncomeOut, status_code=status.HTTP_201_CREATED)
def create_income(payload: IncomeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = _get_owned_wallet(payload.wallet_id, current_user, db, for_update=True)

    now = datetime.now(timezone.utc)
    created_at = datetime.combine(payload.entry_date, now.time(), tzinfo=timezone.utc) if payload.entry_date else now

    income = Income(
        user_id=current_user.id,
        wallet_id=wallet.id,
        wallet_label=wallet.label,
        amount=payload.amount,
        category=payload.category,
        note=payload.note,
        created_at=created_at,
    )
    wallet.balance = Decimal(str(wallet.balance)) + Decimal(str(payload.amount))

    db.add(income)
    db.commit()
    db.refresh(income)
    return income


@app.patch("/api/income/{income_id}", response_model=IncomeOut)
def update_income(
    income_id: int,
    payload: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    income = db.get(Income, income_id)
    if not income or income.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income entry not found")
    updates = payload.model_dump(exclude_unset=True)

    old_amount = Decimal(str(income.amount))
    new_amount = Decimal(str(updates["amount"])) if "amount" in updates else old_amount
    old_wallet_id = income.wallet_id
    new_wallet_id = updates.get("wallet_id", old_wallet_id)

    if new_wallet_id != old_wallet_id:
        if old_wallet_id:
            old_wallet = db.get(Wallet, old_wallet_id, with_for_update=True)
            if old_wallet:
                old_wallet.balance = Decimal(str(old_wallet.balance)) - old_amount
        if new_wallet_id:
            new_wallet = _get_owned_wallet(new_wallet_id, current_user, db, for_update=True)
            new_wallet.balance = Decimal(str(new_wallet.balance)) + new_amount
            updates["wallet_label"] = new_wallet.label
    elif "amount" in updates and income.wallet_id:
        wallet = db.get(Wallet, income.wallet_id, with_for_update=True)
        if wallet:
            delta = new_amount - old_amount
            wallet.balance = Decimal(str(wallet.balance)) + delta

    for field, value in updates.items():
        setattr(income, field, value)
    db.commit()
    db.refresh(income)
    return income


@app.delete("/api/income/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    income = db.get(Income, income_id)
    if not income or income.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income entry not found")

    wallet = db.get(Wallet, income.wallet_id, with_for_update=True) if income.wallet_id else None
    if wallet:
        wallet.balance = Decimal(str(wallet.balance)) - Decimal(str(income.amount))

    db.delete(income)
    db.commit()


# ---------------------------------------------------------------------------
# expenses
# ---------------------------------------------------------------------------
@app.get("/api/expenses", response_model=list[ExpenseOut])
def list_expenses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Expense).where(Expense.user_id == current_user.id).order_by(Expense.created_at.desc())
    return db.scalars(stmt).all()


def _get_owned_expense(expense_id: int, current_user: User, db: Session) -> Expense:
    expense = db.get(Expense, expense_id)
    if not expense or expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


@app.post("/api/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = _get_owned_wallet(payload.wallet_id, current_user, db, for_update=True)

    now = datetime.now(timezone.utc)
    created_at = datetime.combine(payload.entry_date, now.time(), tzinfo=timezone.utc) if payload.entry_date else now

    expense = Expense(
        user_id=current_user.id,
        wallet_id=wallet.id,
        wallet_label=wallet.label,
        amount=payload.amount,
        category=payload.category,
        note=payload.note,
        created_at=created_at,
    )
    wallet.balance = Decimal(str(wallet.balance)) - Decimal(str(payload.amount))

    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@app.patch("/api/expenses/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    expense = _get_owned_expense(expense_id, current_user, db)
    updates = payload.model_dump(exclude_unset=True)

    old_amount = Decimal(str(expense.amount))
    new_amount = Decimal(str(updates["amount"])) if "amount" in updates else old_amount
    old_wallet_id = expense.wallet_id
    new_wallet_id = updates.get("wallet_id", old_wallet_id)

    if new_wallet_id != old_wallet_id:
        if old_wallet_id:
            old_wallet = db.get(Wallet, old_wallet_id, with_for_update=True)
            if old_wallet:
                old_wallet.balance = Decimal(str(old_wallet.balance)) + old_amount
        if new_wallet_id:
            new_wallet = _get_owned_wallet(new_wallet_id, current_user, db, for_update=True)
            new_wallet.balance = Decimal(str(new_wallet.balance)) - new_amount
            updates["wallet_label"] = new_wallet.label
    elif "amount" in updates and expense.wallet_id:
        wallet = db.get(Wallet, expense.wallet_id, with_for_update=True)
        if wallet:
            delta = new_amount - old_amount
            wallet.balance = Decimal(str(wallet.balance)) - delta

    for field, value in updates.items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@app.delete("/api/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = _get_owned_expense(expense_id, current_user, db)

    if expense.wallet_id:
        wallet = db.get(Wallet, expense.wallet_id, with_for_update=True)
        if wallet:
            wallet.balance = Decimal(str(wallet.balance)) + Decimal(str(expense.amount))

    db.delete(expense)
    db.commit()


# ---------------------------------------------------------------------------
# dashboard / safe-to-spend calculation
# ---------------------------------------------------------------------------
@app.get("/api/dashboard", response_model=DashboardOut)
def dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallets = db.scalars(select(Wallet).where(Wallet.user_id == current_user.id)).all()
    recent_expenses = db.scalars(
        select(Expense).where(Expense.user_id == current_user.id).order_by(Expense.created_at.desc()).limit(20)
    ).all()

    total_balance = sum(float(w.balance) for w in wallets)

    today = datetime.now(settings.tzinfo).date()
    if current_user.next_payday and current_user.next_payday > today:
        days_remaining = (current_user.next_payday - today).days
    else:
        days_remaining = 1

    base_daily_allowance = max(total_balance, 0) / days_remaining

    def _local_date(dt: datetime) -> date:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(settings.tzinfo).date()

    spent_today = sum(
        float(e.amount) for e in recent_expenses if _local_date(e.created_at) == today
    )
    safe_to_spend_today = base_daily_allowance - spent_today

    return DashboardOut(
        safe_to_spend_today=round(safe_to_spend_today, 2),
        total_wallet_balance=round(total_balance, 2),
        days_remaining=days_remaining,
        next_payday=current_user.next_payday,
        spent_today=round(spent_today, 2),
        wallets=wallets,
        recent_expenses=recent_expenses,
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}
