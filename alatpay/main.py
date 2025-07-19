import asyncio
import httpx
import os
from alatpay.exceptions import AlatException
from alatpay.models import *
from alatpay.card_transaction import CardPayment, BankTransfer
from dotenv import load_dotenv
from logger.logger import get_logger
from typing import Dict


load_dotenv()
logger = get_logger(__name__) 


class AlatPayIntegration():

    def __init__(self, client: httpx.Client = None):
        self.__subscription_key = os.getenv("ALAT_PAY_PRIMARY_KEY")
        self.__business_id = os.getenv("ALAT_PAY_BUSINESS_ID")
        self.__base_url = os.getenv("ALAT_PAY_BASE_URL")
        self.__client = client or httpx.Client()

        self.__card_transactions = None
        self.__bank_transfer = None

        if not all([self.__subscription_key, self.__business_id, self.__base_url]):
            logger.error("Missing required environment variables for AlatPayIntegration.")
            raise EnvironmentError("Missing required environment variables for AlatPayIntegration")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__client.close()

    def close(self):
        self.__client.close()

    def _get_request(self, path: str, params: Dict = None) -> Dict:
        headers = {
            "Ocp-Apim-Subscription-Key": self.__subscription_key,
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
        headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": self.__subscription_key,
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
            context = e.response.json()
            logger.error(f"HTTP {e.response.status_code} Error: {e.response.json()["message"]}")
            raise AlatException(
                message=context["message"],
                code=e.response.status_code,
                context=context
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

        resp_data = resp.json()
        return resp_data

    @property
    def card_transactions(self) -> AuthResponseModel:
        if self.__card_transactions is None:
            self.__card_transactions = CardPayment(self._post_request, self.__business_id)
        return self.__card_transactions

    @property
    def bank_transfer(self):
        if self.__bank_transfer is None:
            self.__bank_transfer = BankTransfer(
                self._post_request,
                self._get_request,
                self.__business_id
            )
        return self.__bank_transfer
