import requests
import typing
from pyqiwip2p.qiwi_types import QiwiDatetime
from pyqiwip2p.qiwi_types import QiwiCustomer
from pyqiwip2p.qiwi_types import Bill


class QiwiP2P:
	def __init__(self, auth_key: str, currency: str = "RUB"):
		self.auth_key = auth_key
		self.currency = currency

	def bill(self, bill_id: typing.Union[str, int], amount: typing.Union[int, float],
				expiration: typing.Union[str, int, QiwiDatetime] = None,
				customer: QiwiCustomer = None, comment: str = "via pyQiwiP2P made by WhiteApfel"):
		expiration = QiwiDatetime(expiration).qiwi if expiration else QiwiDatetime().expiration()
		amount = str(round(float(amount), 2)) if len(str(float(amount)).split(".")[1]) > 1 else str(round(float(amount), 2))+"0"
		qiwi_request_headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"Authorization": f"Bearer {self.auth_key}"
		}
		qiwi_request_data = {
			"amount": {
				"currency": self.currency,
				"value": amount
			},
			"comment": comment,
			"expirationDateTime": expiration,
			"customer": customer if customer else {},
			"customFields": {}
		}
		print(qiwi_request_headers)
		print(qiwi_request_data)
		qiwi_response = Bill(requests.put(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
					json=qiwi_request_data, headers=qiwi_request_headers))
		return qiwi_response

	def check(self, bill_id: typing.Union[str, int]):
		qiwi_request_headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {self.auth_key}"
		}
		qiwi_response = Bill(requests.get(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
					headers=qiwi_request_headers))
		return qiwi_response

	def reject(self, bill_id: typing.Union[str, int]):
		qiwi_request_headers = {
			"Content-Type": "application/json",
			"Authorization": f"Bearer {self.auth_key}"
		}
		qiwi_response = Bill(requests.post(f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}/reject",
					headers=qiwi_request_headers))
		return qiwi_response


