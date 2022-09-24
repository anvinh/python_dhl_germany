import pytest
from dhl import DHL
from hamcrest import assert_that, equal_to, is_not


@pytest.fixture
def dhl_client():
    return DHL(
        "AUTH_USER",
        "AUTH_PASSWORD",
        "2222222222_01",
        "pass",
        is_test=True,
    )


@pytest.fixture
def shipper():
    return {
        "name": "Something Something GmbH",
        "name2": "",
        "street": "Teststr.",
        "street_number": "1-3",
        "zip": "22089",
        "city": "Hamburg",
        "country_code": "DE",
        "phone": "040251090",
        "email": "test@test.com",
        "contact_person": "Test User",
    }


@pytest.fixture
def receiver():
    return {
        "name": "Test Tester",
        "name2": "TestCompany",
        "street": "Teststraße",
        "street_number": "12",
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

    def test_create_label_DE_packstation(self, dhl_client, shipper, receiver):
        receiver = {
            "name": "User Tester",
            "street": "Packstation",
            "street_number": "168",
            "zip": "60320",
            "city": "Frankfurt",
            "country_code": "DE",
            "phone": "",
            "email": "",
            "care_of_name": None,
            "packing_station": "42124193",
            "account_no": "",
        }

        response = dhl_client.create_shipment_order(
            "123456-1",
            shipper,
            receiver,
            0.3,
            "V01PAK",
            "22222222220101",
        )
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
            "customs": {
                "invoice_no": "1234567",
                "description": "Ziegelsteine",
                "place_of_commital": shipper["city"],
            },
            "positions": [
                {
                    "name": "Test Product 1",
                    "amount": 2,
                    "price": 12.5,
                    "weight_unit": 150,
                    "customs": {
                        "country_code_origin": "DE",
                        "customs_tariff_number": "49119900",
                    },
                },
                {
                    "name": "Test Product 2",
                    "amount": 3,
                    "price": 1.5,
                    "weight_unit": 100,
                    "customs": {
                        "country_code_origin": "DE",
                        "customs_tariff_number": "49119900",
                    },
                },
            ],
        }

        response = dhl_client.create_shipment_order(
            "123456-4",
            shipper,
            receiver,
            6.0,
            "V53WPAK",
            "22222222225301",
            order_to_ship=order,
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

    def test_create_label_CH_ORG(self, dhl_client, shipper, receiver):
        receiver = {
            "name": "User Tester",
            "street": "Bildstrasse, ",
            "street_number": "1",
            "zip": "8580",
            "city": "Amriswil",
            "country_code": "CH",
            "phone": "",
            "email": "",
            "care_of_name": None,
            "packing_station": "",
            "account_no": "",
        }

        order = {
            "order_id": "126bad42dc1",
            "source": "somethingsomething_api",
            "positions": [
                {
                    "product_id": "document",
                    "name": "somethingsomething",
                    "barcode": "dfc4754e",
                    "amount": 2,
                    "weight_unit": 100,
                    "required_shipment": True,
                    "scanned": 2,
                    "price": 2.0,
                    "customs": {
                        "country_code_origin": "DE",
                        "customs_tariff_number": "49119900",
                    },
                }
            ],
            "shipment": {
                "deliveryprovider": "",
                "tracking_no": "",
                "shipped": "",
                "shipped_by_scanstation_id": "",
            },
            "status": {"paid": True, "printed": True, "shipped": False},
            "customs": {
                "invoice_no": "126bad42dc1",
                "description": "somethingsomething",
                "place_of_commital": "Hamburg",
            },
        }

        response = dhl_client.create_shipment_order(
            "123456-5",
            shipper,
            receiver,
            0.4,
            "V53WPAK",
            "22222222225301",
            order_to_ship=order,
        )
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
            response["CreationState"][0]["LabelData"]["Status"][
                "statusMessage"
            ],
            equal_to(
                [
                    "Bitte geben Sie eine Hausnummer an.",
                    "Die eingegebene Adresse ist nicht leitcodierbar.",
                    "Bitte geben Sie eine Hausnummer an.",
                ]
            ),
        )

    def test_create_label_None_content(self, dhl_client, shipper, receiver):
        receiver["district"] = None
        receiver["careOfName"] = None
        receiver["floorNumber"] = None
        receiver["roomNumber"] = None
        receiver["note"] = None

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

    def test_create_label_ES(self, dhl_client, shipper):
        receiver = {
            "name": "Some Fancy Name",
            "name2": "",
            "street": "Cool street",
            "street_number": "123",
            "zip": "35660",
            "city": "Corralejo",
            "country_code": "ES",
            "careOfName": "",
        }

        order = {
            "order_id": "126bad42dc1",
            "source": "somethingsomething_api",
            "positions": [
                {
                    "product_id": "document",
                    "name": "somethingsomething",
                    "barcode": "dfc4754e",
                    "amount": 2,
                    "weight_unit": 100,
                    "required_shipment": True,
                    "scanned": 2,
                    "price": 2.0,
                    "customs": {
                        "country_code_origin": "DE",
                        "customs_tariff_number": "49119900",
                    },
                }
            ],
            "shipment": {
                "deliveryprovider": "",
                "tracking_no": "",
                "shipped": "",
                "shipped_by_scanstation_id": "",
            },
            "status": {"paid": True, "printed": True, "shipped": False},
            "customs": {
                "invoice_no": "126bad42dc1",
                "description": "somethingsomething",
                "place_of_commital": "Hamburg",
            },
        }

        response = dhl_client.create_shipment_order(
            "123456-3",
            shipper,
            receiver,
            0.6,
            "V53WPAK",
            "22222222225301",
            order_to_ship=order,
        )
        # assert_that(response, equal_to("test"))
        assert_that(
            response["CreationState"][0]["LabelData"]["labelUrl"],
            is_not(equal_to(None)),
        )
