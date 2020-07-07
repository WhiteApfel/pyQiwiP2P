from qiwi_types.Errors import QiwiError
from requests import Response
from qiwi_types.Customer import QiwiCustomer


class Bill:
	def __init__(self, response: Response):
		self.r_json = response.json()
		if "errorCode" in self.r_json:
			raise QiwiError(self.r_json)
		else:
			self.site_id: int = self.r_json["siteId"]
			self.bill_id: int = self.r_json["billId"]
			self.amount: float = self.r_json["amount"]["value"]
			self.currency: str = self.r_json["amount"]["currency"]
			self.status: str = self.r_json["status"]["value"]
			self.status_changed: str = self.r_json["status"]["changedDateTime"]
			self.creation: str = self.r_json["creationDateTime"]
			self.expiration: str = self.r_json["expirationDateTime"]
			self.pay_url: str = self.r_json["payUrl"]
			self.comment: str = self.r_json["comment"] if "comment" in self.r_json else None
			self.customer: QiwiCustomer = QiwiCustomer(json_data=self.r_json["customer"]) if "customer" in self.r_json else None
			self.custom_fields: dict = self.r_json["customFields"] if "customFields" in self.r_json else None
			self.json = self.r_json
