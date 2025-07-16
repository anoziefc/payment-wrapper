import asyncio
import httpx
import os
from dotenv import load_dotenv
from logger.logger import get_logger
from paystack.errors import TransactionError
from paystack.models import *
from typing import Dict, Union


load_dotenv()
logger = get_logger(__name__) 


class PayStackIntegration():

    def __init__(self, client: httpx.Client = None):
        self.__secret_key = os.getenv("PAYSTACK_TEST_SECRET_KEY")
        self.__base_url = os.getenv("PAYSTACK_BASE_URL")
        self.__client = client or httpx.Client()

        if not all([self.__secret_key, self.__base_url]):
            logger.error("Missing required environment variables for PayStackIntegration.")
            raise EnvironmentError("Missing required environment variables for PayStackIntegration")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__client.close()

    def close(self):
        self.__client.close()

    def _get_request(self, path: str, params: Dict = None) -> Dict:
        authorization = f"Bearer {self.__secret_key}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization
        }

        try:
            resp = self.__client.get(
                url=f"{self.__base_url}{path}",
                headers=headers,
                params=params if params else None
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        
        retVal = resp.json()
        return retVal


    def _post_request(self, payload: Dict, path: str) -> Dict:
        authorization = f"Bearer {self.__secret_key}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
            "Cache-Control": "no-cache"
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

    def initalize_transaction(self, payload: TransactionsInitPayloadModel, ) -> TransactionsInitResponseModel:
        path = "/transaction/initialize"
        data = payload.model_dump()

        try:
            resp = self._post_request(data, path)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
        
        if resp.get("message") == "Authorization URL created":
            logger.info(f"Authorization URL created success — reference: {resp['data']['reference']}")
            return TransactionsInitResponseModel(**resp)
        else:
            logger.warning(f"Transaction Authorization failed: {resp}")
            raise TransactionError(
                message="Transaction Authorization failed.",
                code=403,
                context={
                    "message": f"{resp.get("message", "")}"
                }
            )

    def verify_transaction(self, reference: str,) -> TransactionsVerifyResponseModel:
        path = f"/transaction/verify/{reference}"

        try:
            resp = self._get_request(path)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
        
        if resp.get("message") == "Verification successful":
            logger.info(f"Transaction Verification success — reference: {resp['data']['reference']}")
            return TransactionsVerifyResponseModel(**resp)
        else:
            logger.warning(f"Card initiation failed: {resp}")
            raise ValueError("Payment initiation failed")

    def list_transactions(self, params: Dict = None) -> ListTransactionsResponseModel:
        path = "/transaction"

        try:
            resp = self._get_request(path, params)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
        
        if resp.get("message") == "Transactions retrieved":
            logger.info(f"Transactions retrieved successfully")
            return ListTransactionsResponseModel(**resp)
        else:
            logger.warning(f"Card initiation failed: {resp}")
            raise ValueError("Payment initiation failed")

    def fetch_transaction(self, id: int) -> ListTransactionResponseModel:
        path = f"/transaction/{id}"

        try:
            resp = self._get_request(path)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
        
        if resp.get("message") == "Transaction retrieved":
            logger.info(f"Transaction retrieved successfully")
            return ListTransactionResponseModel(**resp)
        else:
            logger.warning(f"Card initiation failed: {resp}")
            raise ValueError("Payment initiation failed")
    
    def charge_authorization(self, payload: ChargeAuthorizationPayloadModel) -> ChargeAuthorizationResponseModel:
        path = "/transaction/charge_authorization"
        data = payload.model_dump()
        print(data)

        try:
            resp = self._post_request(data, path)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
        
        if resp.get("message") == "Charge attempted":
            logger.info("Charge attempted")
            return ChargeAuthorizationResponseModel(**resp)
        else:
            logger.warning(f"Transaction Authorization failed: {resp}")
            raise TransactionError(
                message="Transaction Authorization failed.",
                code=403,
                context={
                    "message": f"{resp.get("message", "")}"
                }
            )
    
    def view_transaction_timeline(self, id_or_ref: Union[str, int]) -> Dict:
        path = f"/transaction/timeline/{id_or_ref}"

        try:
            resp = self._get_request(path)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
        
        if resp.get("message") == "Timeline retrieved":
            logger.info(f"Transaction Timeline retrieved successfully")
            return resp
        else:
            logger.warning(f"Card initiation failed: {resp}")
            raise ValueError("Payment initiation failed")


if __name__ == "__main__":
    with PayStackIntegration() as paystack:
        # params = {"customer": 292193195}
        # all_transactions = paystack.list_transactions(**params)
        # print(all_transactions.model_dump_json())
        # transaction = paystack.fetch_transaction(5146531433)
        # print(transaction.model_dump_json())
        # payload = ChargeAuthorizationPayloadModel(
        #     amount="1000",
        #     email="cfanozie@gmail.com",
        #     authorization_code="AUTH_nx33vsiz4q"
        # )
        # charge = paystack.charge_authorization(payload=payload)
        # print(charge)
        time_line = paystack.view_transaction_timeline(5152751671)
        print(time_line)
        # transaction = TransactionsInitPayloadModel(
        #     amount="1000",
        #     email="cfanozie@gmail.com",
        #     channels=["card", "bank", "ussd", "bank_transfer"]
        # )
        # try:
        #     init_transaction = paystack.initalize_transaction(transaction)
        #     init_transaction = init_transaction.model_dump()
        #     print(init_transaction)
        # except Exception as e:
        #     print(f"Error: {e}")
        # reference_num = "87ui7tjf5t"
        # transaction_status = paystack.verify_transaction(reference_num)
        # print(transaction_status.model_dump_json())
