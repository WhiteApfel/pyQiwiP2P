import typing
import re
import time
from datetime import datetime, timedelta, timezone


class QiwiDatetime:
	def __init__(self, moment: typing.Union[str, int, datetime] = None):
		self._exp_regex = r"[0-9]{4}-[01][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9][+-][0-1][0-9]:[0-5][0-9]"
		self.datetime: datetime = self.now_datetime()
		self.qiwi = self.datetime.isoformat()
		self.timestamp = self.datetime.timestamp()
		if moment:
			if type(moment) is str:
				if re.match(self._exp_regex, moment):
					self.set_from_qiwi(moment)
				else:
					raise TypeError("The string does not match the format 'ГГГГ-ММ-ДДTчч:мм:сс+\-чч:мм'")
			if type(moment) is int or type(moment) is float:
				if moment < time.time():
					raise ValueError("Time has passed")
				else:
					self.set_from_timestamp(moment)
			if type(moment) is datetime:
				self.set_from_datetime(moment)
		else:
			self.set_from_datetime(self.now_datetime())

	def now_datetime(self):
		return datetime.now(timezone(timedelta(hours=3))).replace(microsecond=0)

	def timestamp_datetime(self, timestamp: int):
		return datetime.fromtimestamp(timestamp).astimezone(timezone.utc).replace(microsecond=0)

	def timestamp_qiwi(self, timestamp: int):
		return self.timestamp_datetime(timestamp).astimezone(timezone(timedelta(hours=3))).isoformat()

	def datetime_timastamp(self, dt: datetime):
		return int(dt.timestamp())

	def datetime_qiwi(self, dt: datetime):
		return dt.astimezone(timezone(timedelta(hours=3))).replace(microsecond=0).isoformat()

	def qiwi_timestamp(self, dt: str):
		return int(self.qiwi_datetime(dt).timestamp())

	def qiwi_datetime(self, dt: str):
		return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%z")

	def set_from_timestamp(self, timestamp: typing.Union[int, float]):
		self.datetime: datetime = self.timestamp_datetime(int(timestamp))
		self.qiwi = self.timestamp_qiwi(int(timestamp))
		self.timestamp = int(timestamp)

	def set_from_qiwi(self, dt: str):
		self.datetime = self.qiwi_datetime(dt)
		self.qiwi = dt
		self.timestamp = self.qiwi_timestamp(dt)

	def set_from_datetime(self, dt: datetime):
		self.datetime: dt
		self.qiwi = self.datetime_qiwi(dt)
		self.timestamp = self.datetime_timastamp(dt)

	def expiration(self, lifetime: int = 30):
		self.set_from_datetime(self.now_datetime()+timedelta(minutes=lifetime))
		return self.qiwi


