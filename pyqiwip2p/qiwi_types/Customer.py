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
		"""
		Объект пользователя/покупателя. Неизвестно, зачем эта информация нужна QIWI, но раз можно, то почему бы и нет.
		Для удобства работы с QIWI API.
		:param phone: номер телефона практически в любом формате
		:param email: электронная почта
		:param account: идентификатор аккаунта
		:param json_data: dict с полями phone, email и account. При наличии этого параметра, другие игнорируются.
		:param ignore_valid: игнорировать невалидные значения номера телефона и почты
		:param ignore_args: игнорировать отсутствующее значение и поставить None вместо него.
		"""
		if json_data:
			self.phone = json_data["phone"]
			self.email = json_data["email"]
			self.account = json_data["account"]
		else:
			if all([phone, email, account]) or ignore_args:
				if ignore_valid:
					self.phone = str(phone)
					self.email = str(email)
					self.account = str(account)
				else:
					parse_phone = phonenumbers.parse("+"+str(phone))
					if phonenumbers.is_valid_number(parse_phone):
						self.phone = f"+{parse_phone.country_code}{parse_phone.national_number}"
					else:
						ValueError("Customer phone number is not valid")
					self.email = validate_email(email).ascii_email
					self.account = str(account)
			else:
				raise ValueError("One of the values is missing")
		self.dict = {
			"phone": self.phone,
			"email": self.email,
			"account": self.account
		}
