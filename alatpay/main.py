import asyncio
import httpx
import os
from alatpay.errors import CardError
from datetime import datetime
from dotenv import load_dotenv
from logger.logger import get_logger
from pydantic import BaseModel, TypeAdapter, Field, EmailStr
from pydantic.dataclasses import dataclass
from typing import Dict


load_dotenv()
logger = get_logger(__name__) 


@dataclass
class InitPayloadModel:
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
    expiredAt: datetime
    settlementType: str = Field(..., min_length=5)
    createdAt: datetime


class AccountGenerationResponseModel(BaseModel):
    status: bool
    message: str = Field(..., min_length=5)
    data: AccountDetailsModel


class AccountGenerationPayloadModel(BaseModel):
    amount: float
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    orderId: str = Field(..., min_length=5)
    description: str = Field(..., min_length=5)
    customer: CustomerModel


class AlatPayIntegration():

    def __init__(self):
        self.__subscription_key = os.getenv("ALAT_PAY_PRIMARY_KEY")
        self.__business_id = os.getenv("ALAT_PAY_BUSINESS_ID")
        self.__base_url = os.getenv("ALAT_PAY_BASE_URL_DEV")
        self.__client = httpx.Client()

        if not all([self.__subscription_key, self.__business_id, self.__base_url]):
            logger.error("Missing required environment variables for AlatPayIntegration.")
            raise EnvironmentError("Missing required environment variables for AlatPayIntegration")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__client.close()

    def close(self):
        self.__client.close()

    def _post_request(self, payload: Dict, path: str) -> Dict:
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.__subscription_key
        }

        try:
            resp = self.__client.post(
                url=f"{self.__base_url}{path}",
                json=payload,
                headers=headers
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

        resp_data = resp.json()
        return resp_data

    def initiate_card_payment(self, payload: InitPayloadModel) -> InitResponseModel:
        path = "/paymentcard/api/v1/paymentCard/mc/initialize"
        data = TypeAdapter(InitPayloadModel).dump_python(payload)
        data["businessId"] = self.__business_id

        try:
            resp = self._post_request(data, path)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
        
        if resp.get("message") == "Success":
            logger.info(f"Card initiation success — transactionId: {resp['data']['transactionId']}")
            return InitResponseModel(**resp)
        else:
            logger.warning(f"Card initiation failed: {resp}")
            raise ValueError("Payment initiation failed")

    def authenticate_card(self, userData: UserDataModel, payload: InitResponseModel) -> AuthResponseModel:
        path = "/paymentcard/api/v1/paymentCard/mc/authenticate"
        data = payload.model_dump()

        if data.get("gatewayRecommendation", "") == "PROCEED":
            try:
                send_data = userData.model_dump()
                send_data["businessId"] = self.__business_id
                resp = self._post_request(send_data, path)
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise
        else:
            logger.warning(f"Card initiation failed")
            raise CardError(
                message="This card does not meet the required security validations, and so this card cannot not be used to perform this transaction at this time.",
                code=403,
                context={
                    "gatewayRecommendation": f"{data.get("gatewayRecommendation", "")}",
                    "transactionID": f"{data.get("transactionID", "")}"
                }
            )
        
        if resp.get("message") == "Success":
            logger.info(f"Card initiation success — transactionId: {resp['data']['transactionId']}")
            return AuthResponseModel(**resp)
        else:
            logger.warning(f"Card initiation failed: {resp}")
            raise ValueError("Payment initiation failed")

    def generate_virtual_account(self, payload: AccountGenerationPayloadModel) -> AccountGenerationResponseModel:
        path = "/bank-transfer/api/v1/bankTransfer/virtualAccount"
        data = payload.model_dump()
        data["businessId"] = self.__business_id
        
        try:
            resp = self._post_request(data, path)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
        
        if resp.get("message") == "Success":
            logger.info(f"Virtual Account Generation Success — transactionId: {resp['data']['transactionId']}")
            return AccountGenerationResponseModel(**resp)
        else:
            logger.warning(f"Card initiation failed: {resp}")
            raise ValueError("Payment initiation failed")

    def transactions(self):
        pass

def main():
    pass

# Bank Transfer URL: BaseURL/bank-transfer/
# Bank Account URL: BaseURL/alatpayaccountnumber/
# Card URL: BaseURL/paymentcard/

if __name__ == "__main__":
    with AlatPayIntegration() as alat:
        account_request_payload = AccountGenerationPayloadModel(
            amount=0,
            currency="NGN",
            orderId="3fa85f64-5717-4562-b3fc-2c963f66afa6",
            description="Testing Account Generation",
            customer={
                "email": "cfanozie@gmail.com",
                "phone": "08101391054",
                "firstName": "Franklin",
                "lastName": "Anozie",
                "metadata": "Payer"
            }
        )
        try:
            account_generated = alat.generate_virtual_account(account_request_payload)
            print(account_generated)
        except Exception as e:
            print(f"Error: {e}")

# Transaction ID: 999cf73f-4b3c-4161-ae1c-4cf2f17da45e
# Merchant ID: 1ea91ec2-851e-47f1-ac6a-08dcd7e5dac5