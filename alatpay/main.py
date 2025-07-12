import asyncio
import httpx
import os
from dotenv import load_dotenv
from logger.logger import get_logger
from pydantic import BaseModel, TypeAdapter, Field, EmailStr
from pydantic.dataclasses import dataclass
from typing import Dict


load_dotenv()
logger = get_logger(__name__) 

# {
#     "cardNumber": "5123450000000008",
#     "cardMonth": "1",
#     "cardYear": "39",
#     "securityCode": "100",
#     "businessId": "9245fe4a-d402-451c-b9ed-9c1a04247482",
#     "businessName": "string",
#     "amount": 1000.0,
#     "currency": "USD",
#     "orderId": "string",
#     "description": "ALATPay Checkout Payment",
#     "channel": "string",
#     "customer":
#       {
#         "email": "jane.joe@email.com",
#         "phone": "+23480000000001",
#         "firstName": "Jane",
#         "lastName": "+23480000000001",
#         "metadata": "string"
#       },
#     "transactionId": "9245fe4a-d402-451c-b9ed-9c1a04247482"
#   }

@dataclass
class InitPayloadModel:
    cardNumber: str = Field(..., min_length=10)
    currency: str = Field(..., pattern="^[A-Z]{3}$")


class InitResponseModel(BaseModel):
    cardNumber: str = Field(..., min_length=10, max_length=19)
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    gatewayRecommendation: str = Field(..., min_length=3)
    transactionId: str = Field(..., min_length=10)
    orderId: str = Field(..., min_length=10)


class CustomerModel(BaseModel):
        email: EmailStr
        phone: str = Field(..., min_length=8, max_length=15)
        firstName: str = Field(..., min_length=1)
        lastName: str = Field(..., min_length=1)
        metadata: str = Field(..., min_length=1)


class UserDataModel(BaseModel):
    cardNumber: str = Field(..., min_length=10, max_length=19)
    cardMonth: str = Field(..., min_length=2, max_length=2)
    cardYear: str = Field(..., min_length=4, max_length=4)
    securityCode: str = Field(..., min_length=3, max_length=4)
    businessId: str = Field(..., min_length=1)
    businessName: str = Field(..., min_length=1)
    amount: str = Field(..., min_length=2)
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    orderId: str = Field(..., min_length=10)
    description: str = Field(..., min_length=1)
    channel: str = Field(..., min_length=3)
    transactionId: str = Field(..., min_length=10)
    customer: CustomerModel


class AlatPayIntegration():

    def __init__(self):
        self.__subscription_key = os.getenv("ALAT_PAY_PRIMARY_KEY")
        self.__business_id = os.getenv("ALAT_PAY_BUSINESS_ID")
        self.__base_url = os.getenv("ALAT_PAY_BASE_URL")

        if not all([self.__subscription_key, self.__business_id, self.__base_url]):
            raise EnvironmentError("Missing required environment variables for AlatPayIntegration")

    def _post_request(self, client: httpx.Client, payload: Dict, path: str) -> Dict:
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.__subscription_key
        }

        try:
            resp = client.post(
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

    def initiate_card_payment(self, user_data: Dict, payload: InitPayloadModel, client: httpx.Client = None) -> InitResponseModel:
        path = "/api/v1/paymentCard/mc/initialize"
        data = TypeAdapter(InitPayloadModel).dump_python(payload)
        data["businessId"] = self.__business_id

        try:
            if client is None:
                with httpx.Client() as client:
                    resp = self._post_request(client, data, path)
            else:
                resp = self._post_request(client, data, path)
        except Exception as e:
            logger.error(f"An error occured: {e.response.status_code} - {e.response.text}")
            raise
        
        if resp.get("message") == "Success":
            logger.info(f"Card initiation success — transactionId: {resp['transactionId']}")
            return TypeAdapter(InitResponseModel).validate_python(resp.data)
        else:
            logger.warning(f"Card initiation failed: {resp}")
            raise ValueError("Payment initiation failed")

    def authenticate_card(self, payload: InitResponseModel, client: httpx.Client = None) -> bool:
        path = "/api/v1/paymentCard/mc/authenticate"
        data = TypeAdapter(InitResponseModel).dump_python(payload)
        data["businessId"] = self.__business_id

        try:
            if client is None:
                with httpx.Client() as client:
                    resp = self._post_request(client, data, path)
            else:
                resp = self._post_request(client, data, path)
        except Exception as e:
            logger.error(f"An error occured: {e.response.status_code} - {e.response.text}")
            raise
        
        if resp.get("message") == "Success":
            logger.info(f"Card initiation success — transactionId: {resp['transactionId']}")
            return TypeAdapter(InitResponseModel).validate_python(resp.data)
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
    asyncio.run(main())
