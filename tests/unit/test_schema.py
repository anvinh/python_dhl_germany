from hamcrest import assert_that, equal_to, is_not

from dhl import schema


class TestSchema:
    def test_address(self):
        assert_that(schema.Address, equal_to({'name': '', 'street': '', 'street_number': '', 'zip': '', 'city': '',
                    'country_code': '', 'phone': '', 'email': '', 'care_of_name': None, 'packing_station': '', 'account_no': ''}))

    def test_shipment_order(self):
        assert_that(schema.ShipmentOrder, equal_to({'customs': {
                    'invoice_no': '', 'description': '', 'place_of_commital': ''}, 'positions': []}))

    def test_shipment_order_position(self):
        assert_that(schema.ShipmentOrderPosition, equal_to({'name': '', 'amount': 0, 'price': 0, 'weight': 0.0,
                    'weight_unit': 'kg', 'weight_total': 0.0, 'customs': {'country_code_origin': '', 'customs_tariff_number': ''}}))
