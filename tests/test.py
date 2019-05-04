import pytest

from forecaster import Forecaster


def test_day_increase():
    forecaster = Forecaster('2000-06-13', '2000-06-13', 5)
    assert forecaster.day_increase('2000-06-13', 1) == '2000-06-14'
