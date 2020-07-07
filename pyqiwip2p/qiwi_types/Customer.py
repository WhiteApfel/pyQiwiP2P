import typing
import phonenumbers
from email_validator import validate_email, EmailNotValidError


class QiwiCustomer:
	def __init__(self,  phone: typing.Union[str, int] = None,
						email: str = None,
						account: typing.Union[str, int] = None,
						json_data: dict = None,
						ignore_valid: bool = False,
						ignore_args: bool = False):
		if json_data:
			self.phone = json_data["phone"]
			self.email = json_data["email"]
			self.account = json_data["account"]
		else:
			if all([phone, email, account]) or ignore_args:
				if ignore_valid:
					self.phone = str(phone)
					self.email = email
					self.account = str(account)
				else:
					parse_phone = phonenumbers.parse("+"+str(phone))
					if phonenumbers.is_alpha_number(phonenumbers.parse(phone)):
						self.phone = f"+{parse_phone.country_code}{parse_phone.national_number}"
					else:
						ValueError("Customer phone number is not valid")
					self.email = validate_email(email).ascii_email
					self.account = str(account)
			else:
				raise ValueError("One of the values is missing")
