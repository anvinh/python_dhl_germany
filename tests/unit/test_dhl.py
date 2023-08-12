from decouple import config
import pytest
from hamcrest import assert_that, equal_to, raises, calling

from dhl import DHL


@pytest.fixture
def dhl_client():
    return DHL(
        config("DHL_AUTH_USER"),
        config("DHL_AUTH_PASSWORD"),
        "2222222222_01",
        "pass",
        is_test=True,
    )


class TestDHL:
    def test__get_weight_in_kg_kg(self, dhl_client):
        weight = dhl_client._get_weight_in_kg(1000)
        assert_that(weight, equal_to(1000.0))

    def test__get_weight_in_kg_g(self, dhl_client):
        weight = dhl_client._get_weight_in_kg(1000, "g")
        assert_that(weight, equal_to(1.0))

    def test__get_weight_in_kg_default_kg(self, dhl_client):
        weight = dhl_client._get_weight_in_kg(1000)
        assert_that(weight, equal_to(1000.0))

    def test__get_weight_in_kg_None(self, dhl_client):
        weight = dhl_client._get_weight_in_kg(1000, None)
        assert_that(weight, equal_to(1000.0))

    def test__get_weight_in_kg_ValueError(self, dhl_client):
        with pytest.raises(ValueError):
            dhl_client._get_weight_in_kg(1000.0, "t")
