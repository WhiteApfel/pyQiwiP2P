import re
import typing
from datetime import datetime, timedelta, timezone


class QiwiDatetime:
    """
    Тип для удобной работы с форматами времени.

    **Аргументы**

    :param moment: нужный момент времени в одном из удобных форматов для универсализации
    :type moment: ``str``, ``int``, ``datetime``, optional, default=now
    :param lifetime: время жизни счета. Генерирует момент времени с разницей в ``lifetime`` минут. Если указано, параметр ``moment`` игнорируется.
    :type lifetime: ``int``

    **Атрибуты**

    :param datetime: момент времени
    :type datetime: ``datetime.datetime``
    :param qiwi: момент времени
    :type qiwi: ``str`` в формате "*YYYY-MM-DDThh:mm:ss.mss+hh:mm*"
    :param timestamp: момент времени
    :type timestamp: ``int`` в формате unix-времени
    """

    def __init__(
        self, moment: typing.Union[str, int, datetime] = None, lifetime: int = None
    ):
        if lifetime:
            self.expiration(lifetime)
        else:
            self._exp_regex = r"[0-9]{4}-[01][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9].[0-9]{3}[+-][0-1][0-9]:[0-5][0-9]"
            self.datetime: datetime = self.now_datetime()
            self.qiwi = self.datetime.isoformat()
            self.timestamp = self.datetime.timestamp()
            if moment:
                if type(moment) is str:
                    if re.match(self._exp_regex, moment):
                        self.set_from_qiwi(moment)
                    else:
                        raise TypeError(
                            r"The string does not match the format 'ГГГГ-ММ-ДДTчч:мм:сс.мсс+\-чч:мм'"
                        )
                if type(moment) is int or type(moment) is float:
                    self.set_from_timestamp(moment)
                if type(moment) is datetime:
                    self.set_from_datetime(moment)
            else:
                self.set_from_datetime(self.now_datetime())

    def now_datetime(self):
        return datetime.now(timezone(timedelta(hours=3))).replace(microsecond=0)

    def timestamp_datetime(self, timestamp: int):
        return (
            datetime.fromtimestamp(timestamp)
            .astimezone(timezone.utc)
            .replace(microsecond=0)
        )

    def timestamp_qiwi(self, timestamp: int):
        return (
            self.timestamp_datetime(timestamp)
            .astimezone(timezone(timedelta(hours=3)))
            .isoformat()
        )

    def datetime_timastamp(self, dt: datetime):
        return int(dt.timestamp())

    def datetime_qiwi(self, dt: datetime):
        return (
            dt.astimezone(timezone(timedelta(hours=3)))
            .replace(microsecond=0)
            .isoformat()
        )

    def qiwi_timestamp(self, dt: str):
        return int(self.qiwi_datetime(dt).timestamp())

    def qiwi_datetime(self, dt: str):
        return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%z")

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
        """
        Рассчитывает время, когда надо закрыть счет

        :param lifetime: через сколько минут закрыть счет
        :type lifetime: ``int``, optional, default=30
        :return: Время закрытия заказа
        :rtype: ``str`` в формате "*YYYY-MM-DDThh:mm:ss+hh:mm*"
        """
        self.set_from_datetime(self.now_datetime() + timedelta(minutes=lifetime))
