import asyncio
import httpx
from alatpay.exceptions import AlatException
from alatpay.models import (
    AccountGenerationPayloadModel,
    AccountGenerationResponseModel,
    AuthResponseModel,
    InitPayloadModel,
    InitResponseModel,
    UserDataModel
)
from alatpay.utils import assert_success
from logger.logger import get_logger
from typing import Callable, Dict, Optional


logger = get_logger(__name__) 


class CardPayment():

    def __init__(self,
            post_request: Callable[[Dict, str], Dict],
            business_id: str
        ):
        self._post_request = post_request
        self.__business_id = business_id

    def initiate_card_payment(self, payload: InitPayloadModel) -> InitResponseModel:
        path = "/paymentCard/api/v1/paymentCard/mc/initialize"
        data = payload.model_dump()
        data["businessId"] = self.__business_id 

        resp = self._post_request(data, path)

        assert_success(
            resp,
            expected_message="Success",
            error_message="Couldn't Initiate Card Payment",
            error_code=400
        )
        
        logger.info(f"Card initiation success — transactionId: {resp['data']['transactionId']}")
        return InitResponseModel(**resp)

    def authenticate_card(self, userData: UserDataModel, payload: InitResponseModel) -> AuthResponseModel:
        path = "/paymentcard/api/v1/paymentCard/mc/authenticate"
        data = payload.model_dump()

        if data.get("gatewayRecommendation") == "PROCEED":
            send_data = userData.model_dump()
            send_data["businessId"] = self.__business_id
            resp = self._post_request(send_data, path)
        else:
            logger.warning(f"Card initiation failed")
            raise AlatException(
                message="This card does not meet the required security validations, and so this card cannot not be used to perform this transaction at this time.",
                code=400,
                context={
                    "gatewayRecommendation": f"{data.get("gatewayRecommendation", "")}",
                    "transactionID": data.get("transactionID", "")
                }
            )
        
        assert_success(
            resp,
            expected_message="Success",
            error_message="Card Authentication Was Not Successful",
            error_code=400
        )

        logger.info(f"Card initiation success — transactionId: {resp['data']['transactionId']}")
        return AuthResponseModel(**resp)


class BankTransfer():

    def __init__(self,
            post_request: Callable[[Dict, str], Dict],
            get_request: Callable[[str, Optional[Dict]], Dict],
            business_id: str
        ):
        self._post_request = post_request
        self.__get_request = get_request
        self.__business_id = business_id

    def generate_virtual_account(self, payload: AccountGenerationPayloadModel) -> AccountGenerationResponseModel:
        path = "/bank-transfer/api/v1/bankTransfer/virtualAccount"
        data = payload.model_dump()
        data["businessId"] = self.__business_id

        resp = self._post_request(data, path)

        assert_success(
            resp,
            expected_message="Business fetched locally",
            error_message="Failed to create virtual account",
            error_code=400
        )

        logger.info(f"Virtual Account Generation Success — transactionId: {resp['data']['transactionId']}")
        return AccountGenerationResponseModel(**resp)
    
    def confirm_transaction_status(self, transaction_id: str) -> AccountGenerationResponseModel:
        path = f"/bank-transfer/api/v1/bankTransfer/transactions/{transaction_id}"

        resp = self.__get_request(path)
        return resp
