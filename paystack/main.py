import asyncio
import httpx
import os
from dotenv import load_dotenv
from logger.logger import get_logger
from paystack.transactions.handler import TransactionHandler 
from typing import Dict


load_dotenv()
logger = get_logger(__name__) 


class PayStackIntegration():

    def __init__(self, client: httpx.Client = None):
        self.__secret_key = os.getenv("PAYSTACK_TEST_SECRET_KEY")
        self.__base_url = os.getenv("PAYSTACK_BASE_URL")
        self.__client = client or httpx.Client()

        self.__transactions = None

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
            "Authorization": authorization,
            "Cache-Control": "no-cache"
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

    @property
    def transactions(self) -> TransactionHandler:
        if self.__transactions is None:
            self.__transactions = TransactionHandler(
                post_request=self._post_request,
                get_request=self._get_request
            )
        return self.__transactions



if __name__ == "__main__":
    pass