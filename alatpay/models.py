from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, Optional


class InitPayloadModel(BaseModel):
    cardNumber: str = Field(..., min_length=10)
    currency: str = Field(..., pattern="^[A-Z]{3}$")


class InitResponseModel(BaseModel):
    status: bool
    message: str
    gatewayRecommendation: str = Field(..., min_length=3)
    transactionId: str = Field(..., min_length=5)
    orderId: str = Field(..., min_length=5)


class CustomerModel(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=11, max_length=14)
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    metadata: str = Field(..., min_length=1)


class UserDataModel(BaseModel):
    cardNumber: str = Field(..., min_length=10, max_length=19)
    cardMonth: str = Field(..., min_length=1, max_length=2)
    cardYear: str = Field(..., min_length=2, max_length=4)
    securityCode: str = Field(..., min_length=3, max_length=4)
    businessName: str = Field(..., min_length=1)
    amount: str = Field(..., min_length=2)
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    orderId: str = Field(..., min_length=5)
    description: str = Field(..., min_length=1)
    channel: str = Field(..., min_length=3)
    transactionId: str = Field(..., min_length=5)
    customer: CustomerModel


class AuthResponseModel(BaseModel):
    status: bool
    message: str = Field(..., min_length=5)
    redirectHtml: str = Field(..., min_length=5)
    gatewayRecommendation: str = Field(..., min_length=5)
    transactionId: str = Field(..., min_length=5)
    orderId: str = Field(..., min_length=5)


class AccountDetailsModel(BaseModel):
    businessId: str = Field(..., min_length=5)
    amount: float
    currency: str = Field(..., min_length=5)
    orderId: str = Field(..., min_length=5)
    description: str = Field(..., min_length=5)
    customer: CustomerModel
    id: str = Field(..., min_length=5)
    merchantId: str = Field(..., min_length=5)
    virtualBankCode: str = Field(..., min_length=5)
    virtualBankAccountNumber: str = Field(..., min_length=5)
    businessBankAccountNumber: str = Field(..., min_length=5)
    businessBankCode: str = Field(..., min_length=5)
    transactionId: str = Field(..., min_length=5)
    status: str = Field(..., min_length=5)
    expiredAt: Optional[datetime]
    settlementType: str = Field(..., min_length=5)
    createdAt: Optional[datetime]


class AccountGenerationResponseModel(BaseModel):
    status: bool
    message: str = Field(..., min_length=5)
    data: AccountDetailsModel


class AccountGenerationPayloadModel(BaseModel):
    amount: float
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    orderId: str = Field(..., min_length=2)
    description: str = Field(..., min_length=2)
    customer: CustomerModel