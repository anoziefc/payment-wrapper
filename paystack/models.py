from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Dict, List, Optional, Annotated, Any


ReferenceStr = Annotated[
    str,
    Field(
        patterm=r'^[\w\-=.]+$',
        description="Unique transaction reference. Only -, ., = and alphanumeric characters allowed"
    )
]

BearerStr = Annotated[
    str,
    Field(
        pattern=r'^(account|subaccount)$',
        description="Who bears the transaction charges: account or subaccount"
    )
]


class TransactionsInitPayloadModel(BaseModel):
    amount: str = Field(..., description="Amount in the subunit of the supported currency")
    email: EmailStr = Field(..., description="Customer's email address")

    currency: Optional[str] = Field(None, description="Transaction currency (defaults to integration currency)")
    reference: Optional[ReferenceStr] = None
    callback_url: Optional[HttpUrl] = Field(
        None, description="Fully qualified URL to override the dashboard callback URL"
    )
    plan: Optional[str] = Field(None, description="Plan code for subscription. Overrides amount if provided")
    invoice_limit: Optional[int] = Field(
        None, description="Number of times to charge customer during plan subscription"
    )
    metadata: Optional[str] = Field(
        None, description="Stringified JSON object of custom metadata"
    )
    channels: Optional[List[str]] = Field(
        None, description="List of payment channels (e.g. card, bank, apple_pay, ussd, qr, mobile_money, bank_transfer, eft)"
    )
    split_code: Optional[str] = Field(None, description="Split code of the transaction split")
    subaccount: Optional[str] = Field(None, description="Code for the subaccount that owns the payment")
    transaction_charge: Optional[int] = Field(
        None, description="Overrides split configuration. Amount goes to main account"
    )
    bearer: Optional[BearerStr] = None


class TransactionInitResponseDataModel(BaseModel):
    authorization_url: HttpUrl
    access_code: str
    reference: str


class TransactionsInitResponseModel(BaseModel):
    status: bool
    message: str
    data: TransactionInitResponseDataModel


class CustomField(BaseModel):
    display_name: str
    variable_name: str
    value: str


class CustomerMetadata(BaseModel):
    custom_fields: Optional[List[CustomField]] = None


class CustomerData(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    email: EmailStr
    customer_code: str
    phone: Optional[str]
    metadata: Optional[CustomerMetadata] = None
    risk_action: str
    international_format_phone: Optional[str] = None


class LogHistory(BaseModel):
    type: str
    message: str
    time: int


class Log(BaseModel):
    start_time: int
    time_spent: int
    attempts: int
    errors: int
    success: bool
    mobile: bool
    input: List[Any]
    history: List[LogHistory]


class AuthorizationData(BaseModel):
    authorization_code: Optional[str] = None
    bin: Optional[str] = None
    last4: Optional[str] = None
    exp_month: Optional[str] = None
    exp_year: Optional[str] = None
    channel: Optional[str] = None
    card_type: Optional[str] = None
    bank: Optional[str] = None
    country_code: Optional[str] = None
    brand: Optional[str] = None
    reusable: Optional[bool] = None
    signature: Optional[str] = None
    account_name: Optional[str] = None


class TransactionVerifyData(BaseModel):
    id: int
    domain: str
    status: str
    reference: str
    receipt_number: Optional[str]
    amount: int
    message: Optional[str]
    gateway_response: str
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    channel: str
    currency: str
    ip_address: str
    metadata: Optional[Any]
    log: Optional[Log]
    fees: Optional[int] = None
    fees_split: Optional[Any]
    authorization: Optional[AuthorizationData] = None
    customer: CustomerData
    plan: Optional[Any]
    split: Optional[Dict[str, Any]]
    order_id: Optional[str]
    paidAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    requested_amount: int
    pos_transaction_data: Optional[Any]
    source: Optional[Any]
    fees_breakdown: Optional[Any]
    connect: Optional[Any]
    transaction_date: Optional[datetime] = None
    plan_object: Optional[Dict[str, Any]]
    subaccount: Optional[Dict[str, Any]]


class ListTransactionsDataModel(BaseModel):
    id: int
    domain: str
    status: str
    reference: str
    amount: int
    message: Optional[str]
    gateway_response: str
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    channel: str
    currency: str
    ip_address: str
    metadata: Optional[Any]
    log: Optional[Log]
    fees: Optional[int] = None
    fees_split: Optional[Any]
    authorization: Optional[AuthorizationData] = None
    customer: CustomerData
    plan: Optional[Any]
    split: Optional[Dict[str, Any]]
    order_id: Optional[str]
    paidAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    requested_amount: int
    pos_transaction_data: Optional[Any]
    source: Optional[Any]
    connect: Optional[Any]
    subaccount: Optional[Dict[str, Any]]


class ListTransactionsResponseModel(BaseModel):
    status: bool
    message: str
    data: List[ListTransactionsDataModel]
    meta: Optional[Dict[str, Any]]


class ListTransactionResponseModel(BaseModel):
    status: bool
    message: str
    data: ListTransactionsDataModel


class TransactionsVerifyResponseModel(BaseModel):
    status: bool
    message: str
    data: TransactionVerifyData


class ChargeAuthorizationPayloadModel(BaseModel):
    amount: str = Field(..., description="Amount in the subunit of the supported currency")
    email: EmailStr = Field(..., description="Customer's email address")
    authorization_code: str = Field(..., description="Valid authorization code to charge")

    reference: Optional[ReferenceStr] = Field(
        None, description="Unique transaction reference. Only -, ., = and alphanumeric characters allowed."
    )
    currency: Optional[str] = Field(None, description="Currency in which amount should be charged.")
    metadata: Optional[str] = Field(
        None,
        description='Stringified JSON with optional "custom_fields". E.g. {"custom_fields":[{"display_name":"Cart ID","variable_name":"cart_id","value":"8393"}]}'
    )
    channels: Optional[List[str]] = Field(
        None,
        description="Options to show user: e.g. ['card'], ['bank'], or ['card','bank']"
    )
    subaccount: Optional[str] = Field(
        None,
        description="The code for the subaccount that owns the payment. e.g. ACCT_xxxx"
    )
    transaction_charge: Optional[int] = Field(
        None,
        description="Flat fee to charge subaccount for this transaction (subunit of currency). Overrides split %."
    )
    bearer: Optional[BearerStr] = Field(
        None,
        description='Who bears Paystack charges: "account" or "subaccount" (defaults to "account").'
    )
    queue: Optional[bool] = Field(
        None,
        description="Set to true to queue scheduled charge calls."
    )


class ChargeData(BaseModel):
    id: int
    amount: int
    currency: str
    transaction_date: Optional[datetime] = None
    status: str
    reference: str
    domain: str
    metadata: Optional[Any] = None
    gateway_response: str
    message: Optional[str] = None
    channel: str
    ip_address: Optional[str] = None
    log: Optional[Any] = None
    fees: Optional[int] = None
    authorization: Optional[AuthorizationData] = None
    customer: Optional[CustomerData] = None
    plan: Optional[Any] = None


class ChargeAuthorizationResponseModel(BaseModel):
    status: bool
    message: str
    data: ChargeData
