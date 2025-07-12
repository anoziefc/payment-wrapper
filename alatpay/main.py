import asyncio
import httpx
import os
from alatpay.errors import CardError
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
    businessId: str = Field(..., min_length=1)
    businessName: str = Field(..., min_length=1)
    amount: str = Field(..., min_length=2)
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    orderId: str = Field(..., min_length=5)
    description: str = Field(..., min_length=1)
    channel: str = Field(..., min_length=3)
    transactionId: str = Field(..., min_length=5)
    customer: CustomerModel


class AuthResponseModel(BaseModel):
    redirectHtml: str = Field(..., min_length=5)
    gatewayRecommendation: str = Field(..., min_length=5)
    transactionId: str = Field(..., min_length=5)
    orderId: str = Field(..., min_length=5)


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
            return InitResponseModel(**resp["data"])
        else:
            logger.warning(f"Card initiation failed: {resp}")
            raise ValueError("Payment initiation failed")

    def authenticate_card(self, userData: UserDataModel, payload: InitResponseModel) -> AuthResponseModel:
        path = "/paymentcard/api/v1/paymentCard/mc/authenticate"
        data = payload.model_dump()

        if data.get("gatewayRecommendation", "") == "PROCEED":
            try:
                send_data = userData.model_dump()
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
            return AuthResponseModel(**resp["data"])
        else:
            logger.warning(f"Card initiation failed: {resp}")
            raise ValueError("Payment initiation failed")

    def confirm_payment(self):
        pass

    def transactions(self):
        pass

def main():
    pass


# Bank Transfer URL: BaseURL/bank-transfer/
# Bank Account URL: BaseURL/alatpayaccountnumber/
# Card URL: BaseURL/paymentcard/

if __name__ == "__main__":
    with AlatPayIntegration() as alat:
        init_payload = InitPayloadModel(
            cardNumber="1234567890123456",
            currency="NGN"
        )
        try:
            init_resp = alat.initiate_card_payment(init_payload)

            user_data = UserDataModel(
                cardNumber="1234567890123456",
                cardMonth="01",
                cardYear="2026",
                securityCode="123",
                businessId=os.getenv("ALAT_PAY_BUSINESS_ID"),
                businessName="Example Corp",
                amount="1000",
                currency="NGN",
                orderId=init_resp.orderId,
                description="Test Transaction",
                channel="web",
                transactionId=init_resp.transactionId,
                customer=CustomerModel(
                    email="test@example.com",
                    phone="08012345678",
                    firstName="John",
                    lastName="Doe",
                    metadata="tester"
                )
            )

            auth_resp = alat.authenticate_card(user_data, init_resp)
            print(auth_resp.redirectHtml)
        except Exception as e:
            print(f"Error: {e}")

