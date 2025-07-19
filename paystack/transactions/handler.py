import asyncio
from logger.logger import get_logger
from paystack.errors.errors import TransactionError
from paystack.models import *
from paystack.utils.response import assert_success
from typing import Callable, Dict, Union, Optional


logger = get_logger(__name__) 


class TransactionHandler():

    def __init__(self,
            post_request: Callable[[Dict, str], Dict],
            get_request: Callable[[str, Optional[Dict]], Dict]
        ):
        self._post_request = post_request
        self._get_request = get_request

    def initialize_transaction(self, payload: TransactionsInitPayloadModel, ) -> TransactionsInitResponseModel:
        path = "/transaction/initialize"
        data = payload.model_dump()

        resp = self._post_request(data, path)

        assert_success(
            resp,
            expected_message="Authorization URL created",
            error_message="Transaction Authorization failed"
        )

        logger.info(f"Authorization URL created success — reference: {resp['data']['reference']}")
        return TransactionsInitResponseModel(**resp)


    def verify_transaction(self, reference: str,) -> TransactionsVerifyResponseModel:
        path = f"/transaction/verify/{reference}"

        resp = self._get_request(path)

        assert_success(
            resp,
            expected_message="Authorization URL created",
            error_message="Transaction Authorization failed"
        )

        if resp.get("message") == "Verification successful":
            logger.info(f"Transaction Verification success — reference: {resp['data']['reference']}")
            return TransactionsVerifyResponseModel(**resp)
        else:
            logger.warning(f"Transaction Verification failed: {resp.get('message')}")
            raise TransactionError(
                message="Transaction Verification failed.",
                code=403,
                context={
                    "message": resp.get('message', '')
                }
            )

    def list_transactions(self, params: Dict = None) -> ListTransactionsResponseModel:
        path = "/transaction"

        resp = self._get_request(path, params)

        assert_success(
            resp,
            expected_message="Authorization URL created",
            error_message="Transaction Authorization failed"
        )

        if resp.get("message") == "Transactions retrieved":
            logger.info(f"Transactions retrieved successfully")
            return ListTransactionsResponseModel(**resp)
        else:
            logger.warning(f"Transactions retrieval failed: {resp.get('message')}")
            raise TransactionError(
                message="Transactions retrieval failed.",
                code=403,
                context={
                    "message": resp.get('message', '')
                }
            )

    def fetch_transaction(self, id: int) -> ListTransactionResponseModel:
        path = f"/transaction/{id}"

        resp = self._get_request(path)

        assert_success(
            resp,
            expected_message="Authorization URL created",
            error_message="Transaction Authorization failed"
        )
                
        if resp.get("message") == "Transaction retrieved":
            logger.info(f"Transaction retrieved successfully")
            return ListTransactionResponseModel(**resp)
        else:
            logger.warning(f"Transaction retrieval failed: {resp.get('message')}")
            raise TransactionError(
                message="Transaction retrieval failed.",
                code=403,
                context={
                    "message": resp.get('message', '')
                }
            )
    
    def charge_authorization(self, payload: ChargeAuthorizationPayloadModel) -> ChargeAuthorizationResponseModel:
        path = "/transaction/charge_authorization"
        data = payload.model_dump()

        resp = self._post_request(data, path)
        
        if resp.get("message") == "Charge attempted":
            logger.info("Charge attempted successfully")
            return ChargeAuthorizationResponseModel(**resp)
        else:
            logger.warning(f"Charge attempt failed: {resp.get('message')}")
            raise TransactionError(
                message="Charge attempt failed.",
                code=403,
                context={
                    "message": resp.get('message', '')
                }
            )
    
    def view_transaction_timeline(self, id_or_ref: Union[str, int]) -> Dict:
        path = f"/transaction/timeline/{id_or_ref}"

        resp = self._get_request(path)

        if resp.get("message") == "Timeline retrieved":
            logger.info(f"Transaction Timeline retrieved successfully")
            return resp
        else:
            logger.warning(f"Transaction Timeline retrieval failed: {resp.get('message')}")
            raise TransactionError(
                message="Transaction Timeline retrieval failed.",
                code=403,
                context={
                    "message": resp.get('message', '')
                }
            )

    def transaction_totals(self, params: Dict = None) -> TransactionsTotalResponseModel:
        path = f"/transaction/totals"

        resp = self._get_request(path, params=params)
        
        if resp.get("message") == "Transaction totals":
            logger.info(f"Transactions totals retrieved successfully")
            return TransactionsTotalResponseModel(**resp)
        else:
            logger.warning(f"Transactions totals retrieval failed: {resp.get('message')}")
            raise TransactionError(
                message="Transactions totals retrieval failed.",
                code=403,
                context={
                    "message": resp.get('message', '')
                }
            )

    
    def export_transactions(self, params: Dict = None) -> ExportTransactionsResponseModel:
        path = f"/transaction/export"

        resp = self._get_request(path, params=params)
        
        
        if resp.get("message") == "Export successful":
            logger.info(f"Transactions Export successful")
            return ExportTransactionsResponseModel(**resp)
        else:
            logger.warning(f"Transactions Export failed: {resp.get('message')}")
            raise TransactionError(
                message="Transactions Export failed.",
                code=403,
                context={
                    "message": resp.get('message', '')
                }
            )

    
    def partial_debit(self, payload: PartialDebitPayload) -> PartialDebitResponseModel:
        path = f"/transaction/partial_debit"
        data = payload.model_dump()

        resp = self._post_request(data, path)
        
        if resp.get("message") == "Charge attempted":
            logger.info(f"Partial Debit successful")
            return PartialDebitResponseModel(**resp)
        else:
            logger.warning(f"Partial Debit failed: {resp.get('message')}")
            raise TransactionError(
                message="Partial Debit failed.",
                code=403,
                context={
                    "message": resp.get('message', '')
                }
            )



if __name__ == "__main__":
    with TransactionHandler() as paystack:
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
        payload = PartialDebitPayload(
            authorization_code="AUTH_nx33vsiz4q",
            currency="NGN",
            amount="1000",
            email="cfanozie@gmail.com"
        )
        part_pay = paystack.partial_debit(payload=payload)
        print(part_pay)
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
