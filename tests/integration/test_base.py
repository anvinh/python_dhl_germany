import pytest
from dhl import DHL
from hamcrest import assert_that, equal_to, is_not


@pytest.fixture
def dhl_client():
    return DHL('jep01', 'pKy8WplDuA86byh-!SzZf8', '2222222222_01', 'pass', is_test=True)


@pytest.fixture
def shipper():
    return {
        'name': 'Albert Bauer Print! GmbH & Co. KG',
        'name2': '',
        'street': 'Conventstraße',
        'street_number': '1-3',
        'zip': '22089',
        'city': 'Hamburg',
        'country_code': 'DE',
        'phone': '040251090',
        'email': 'order@albertbauerprint.com',
        'contact_person': 'Sven Roedemester',
    }


@pytest.fixture
def receiver():
    return {
        'name': 'Test Tester',
        'name2': 'TestCompany',
        'street': 'Kommodore-Johnsen-Boulevard',
        'street_number': '32',
        'zip': '28217',
        'city': 'Bremen',
        'country_code': 'DE',
        'careOfName': ''
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
        #assert_that(response, equal_to("test"))
        assert_that(response["CreationState"][0]["LabelData"]["labelUrl"], is_not(equal_to("")))


    def test_create_label_DE_Warensendung(self):
        pass

    def test_create_label_EU(self):
        pass

    def test_create_label_CH(self):
        pass

    def test_create_label_force(self):
        pass

    def test_create_label_wrong(self):
        pass
