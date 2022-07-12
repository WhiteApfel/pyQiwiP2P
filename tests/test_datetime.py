import time
from datetime import timedelta
from typing import Union

import pytest

from pyqiwip2p.p2p_types import QiwiDatetime


@pytest.mark.parametrize("lifetime", [2, 13, 33, 20, 30])
def test_datetime_lifetime(lifetime: int):
    assert (
        abs(QiwiDatetime(lifetime=lifetime).timestamp - time.time() - lifetime * 60) < 1
    )


@pytest.mark.xfail
@pytest.mark.parametrize(
    "lifetime", ["24", (24,), [24], {24}, {24: 25}, timedelta(minutes=15)]
)
def test_datetime_lifetime_fail(lifetime):
    assert (
        abs(QiwiDatetime(lifetime=lifetime).timestamp - time.time() - lifetime * 60) < 1
    )


def test_datetime_eq():
    now = QiwiDatetime()
    assert QiwiDatetime(now.datetime).datetime == now.datetime
    assert QiwiDatetime(now.timestamp).datetime == now.datetime
    assert QiwiDatetime(now.datetime).timestamp == now.timestamp
    assert QiwiDatetime(now.timestamp).timestamp == now.timestamp
    assert QiwiDatetime(now.datetime).qiwi == now.qiwi
    assert QiwiDatetime(now.timestamp).qiwi == now.qiwi


@pytest.mark.parametrize("timestamp", [1626910525.833006, 1626910525, 1626910535])
def test_datetime_timestamp(timestamp):
    assert QiwiDatetime(timestamp).timestamp == int(timestamp)


@pytest.mark.xfail
@pytest.mark.parametrize(
    "timestamp", [1626910525.833006, "1626910525", [1626910535], b"1626910535"]
)
def test_datetime_timestamp_fail(timestamp):
    assert QiwiDatetime(timestamp).timestamp == timestamp
