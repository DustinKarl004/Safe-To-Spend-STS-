from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

INCOME_CATEGORY_PATTERN = "^(salary|interest|investment|cashback|allowance|bonus|other)$"


# ---- auth ----
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginOut(BaseModel):
    access_token: str | None = None
    token_type: str = "bearer"
    requires_2fa: bool = False
    mfa_token: str | None = None


class MfaLoginRequest(BaseModel):
    mfa_token: str
    code: str = Field(min_length=6, max_length=6)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class TwoFactorSetupOut(BaseModel):
    secret: str
    otpauth_uri: str
    qr_code_data_uri: str


class TwoFactorVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class TwoFactorDisableRequest(BaseModel):
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    next_payday: date | None = None
    payday_amount: float | None = None
    payday_wallet_id: int | None = None
    payday_category: str | None = None
    payday_note: str | None = None
    totp_enabled: bool = False


# ---- payday ----
class PaydayUpdate(BaseModel):
    next_payday: date | None = None
    amount: float | None = Field(default=None, ge=0)
    wallet_id: int | None = None
    category: str | None = Field(default=None, pattern=INCOME_CATEGORY_PATTERN)
    note: str | None = Field(default=None, max_length=140)


# ---- wallets ----
class WalletCreate(BaseModel):
    kind: str = Field(pattern="^(ewallet|digital_bank|bank|cash)$")
    label: str = Field(max_length=50)
    balance: float = Field(ge=0)


class WalletUpdate(BaseModel):
    label: str | None = Field(default=None, max_length=50)
    balance: float | None = Field(default=None, ge=0)


class WalletOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    kind: str
    label: str
    balance: float


class WalletAdjustmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    wallet_id: int
    wallet_label: str
    delta: float
    created_at: datetime


# ---- income ----
class IncomeCreate(BaseModel):
    wallet_id: int
    amount: float = Field(gt=0)
    category: str = Field(pattern=INCOME_CATEGORY_PATTERN)
    note: str | None = Field(default=None, max_length=140)
    entry_date: date | None = None


class IncomeUpdate(BaseModel):
    wallet_id: int | None = None
    amount: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, pattern=INCOME_CATEGORY_PATTERN)
    note: str | None = Field(default=None, max_length=140)


class IncomeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    wallet_id: int | None
    wallet_label: str
    amount: float
    category: str
    note: str | None
    created_at: datetime


# ---- expenses ----
CATEGORY_PATTERN = (
    "^(food|groceries|transpo|bills|shopping|entertainment|games|health|education"
    "|personal_care|home|travel|subscriptions|gifts|tithes|pets|misc|other)$"
)


class ExpenseCreate(BaseModel):
    wallet_id: int
    amount: float = Field(gt=0)
    category: str = Field(pattern=CATEGORY_PATTERN)
    note: str | None = Field(default=None, max_length=140)
    entry_date: date | None = None


class ExpenseUpdate(BaseModel):
    wallet_id: int | None = None
    amount: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, pattern=CATEGORY_PATTERN)
    note: str | None = Field(default=None, max_length=140)


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    wallet_id: int | None
    wallet_label: str | None
    amount: float
    category: str
    note: str | None
    created_at: datetime


# ---- dashboard ----
class DashboardOut(BaseModel):
    safe_to_spend_today: float
    total_wallet_balance: float
    days_remaining: int
    next_payday: date | None
    spent_today: float
    wallets: list[WalletOut]
    recent_expenses: list[ExpenseOut]
