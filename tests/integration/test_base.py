import pytest
from dhl import DHL
from hamcrest import assert_that, equal_to, is_not


@pytest.fixture
def dhl_client():
    return DHL(
        "jep01",
        "pKy8WplDuA86byh-!SzZf8",
        "2222222222_01",
        "pass",
        is_test=True,
    )


@pytest.fixture
def shipper():
    return {
        "name": "Albert Bauer Print! GmbH & Co. KG",
        "name2": "",
        "street": "Conventstraße",
        "street_number": "1-3",
        "zip": "22089",
        "city": "Hamburg",
        "country_code": "DE",
        "phone": "040251090",
        "email": "order@albertbauerprint.com",
        "contact_person": "Sven Roedemester",
    }


@pytest.fixture
def receiver():
    return {
        "name": "Test Tester",
        "name2": "TestCompany",
        "street": "Kommodore-Johnsen-Boulevard",
        "street_number": "32",
        "zip": "28217",
        "city": "Bremen",
        "country_code": "DE",
        "careOfName": "",
    }


class TestDHL:
    def test_create_label_DE(self, dhl_client, shipper, receiver):
        response = dhl_client.create_shipment_order(
            "123456-1",
            shipper,
            receiver,
            0.3,
            "V01PAK",
            "22222222220101",
        )
        # assert_that(response, equal_to("test"))
        assert_that(
            response["CreationState"][0]["LabelData"]["labelUrl"],
            is_not(equal_to(None)),
        )

    def test_create_label_DE_Warensendung(self, dhl_client, shipper, receiver):
        response = dhl_client.create_shipment_order(
            "123456-2",
            shipper,
            receiver,
            0.5,
            "V62WP",
            "22222222226201",
        )
        # assert_that(response, equal_to("test"))
        assert_that(
            response["CreationState"][0]["LabelData"]["labelUrl"],
            is_not(equal_to(None)),
        )

    def test_create_label_EU(self, dhl_client, shipper):
        receiver = {
            "name": "Test Tester",
            "name2": "",
            "street": "Praterstrasse",
            "street_number": "72",
            "zip": "1020",
            "city": "Wien",
            "country_code": "AT",
            "careOfName": "",
        }

        response = dhl_client.create_shipment_order(
            "123456-3",
            shipper,
            receiver,
            0.6,
            "V53WPAK",
            "22222222225301",
        )
        # assert_that(response, equal_to("test"))
        assert_that(
            response["CreationState"][0]["LabelData"]["labelUrl"],
            is_not(equal_to(None)),
        )

    def test_create_label_CH(self, dhl_client, shipper, receiver):
        receiver = {
            "name": "Test Tester",
            "name2": "",
            "street": "Kohlenberg",
            "street_number": "17",
            "zip": "4051",
            "city": "Basel",
            "country_code": "CH",
            "careOfName": "",
        }

        order = {
            "invoice_no": "1234567",
            "description": "Ziegelsteine",
            "place_of_commital": shipper["city"],
            "positions": [
                {
                    "name": "Test Product 1",
                    "country_code_origin": "DE",
                    "customs_tariff_number": "49119900",
                    "quantity": 2,
                    "price": 12.5,
                    "weight_per_unit": 0.3
                },
                {
                    "name": "Test Product 2",
                    "country_code_origin": "DE",
                    "customs_tariff_number": "49119900",
                    "quantity": 3,
                    "price": 1.5,
                    "weight_per_unit": 0.5
                }
            ]
        }

        response = dhl_client.create_shipment_order(
            "123456-4",
            shipper,
            receiver,
            3.0,
            "V53WPAK",
            "22222222225301",
            order_to_ship=order
        )
        # assert_that(response, equal_to("test"))
        assert_that(
            response["CreationState"][0]["LabelData"]["labelUrl"],
            is_not(equal_to(None)),
        )
        assert_that(
            response["CreationState"][0]["LabelData"]["exportLabelUrl"],
            is_not(equal_to(None)),
        )

    """
    NOT TESTABLE YET
    def test_create_label_force(self, dhl_client, shipper, receiver):
        receiver["street"] = "Teststr."
        receiver["street_number"] = "Number"
        print(receiver)
        response = dhl_client.create_shipment_order(
            "123456-5",
            shipper,
            receiver,
            0.3,
            "V01PAK",
            "22222222220101",
        )
        assert_that(response, equal_to("test"))
        assert_that(
            response["CreationState"][0]["LabelData"]["labelUrl"],
            equal_to(None),
        )

        response = dhl_client.create_shipment_order(
            "123456-5",
            shipper,
            receiver,
            0.3,
            "V01PAK",
            "22222222220101",
            force_print=True,
        )
        assert_that(
            response["CreationState"][0]["LabelData"]["labelUrl"],
            is_not(equal_to(None)),
        )
    """

    def test_create_label_error(self, dhl_client, shipper, receiver):
        receiver["street_number"] = ""
        response = dhl_client.create_shipment_order(
            "123456-5",
            shipper,
            receiver,
            0.3,
            "V01PAK",
            "22222222220101",
        )
        assert_that(
            response["CreationState"][0]["LabelData"]["labelUrl"],
            equal_to(None),
        )
        assert_that(
            response["CreationState"][0]["LabelData"]["Status"]["statusMessage"],
            equal_to([
                'Bitte geben Sie eine Hausnummer an.',
                'Die eingegebene Adresse ist nicht leitcodierbar.',
                'Bitte geben Sie eine Hausnummer an.'
            ]),
        )
