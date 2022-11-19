import json


Address = {
    "name": "",  # firstname lastname
    "street": "",
    "street_number": "",
    "zip": "",
    "city": "",
    "country_code": "",  # DE, AT, CH, FR, ...
    "phone": "",  # (opt)
    "email": "",  # (opt)
    "care_of_name": None,  # (opt)
    "packing_station": "",  # (opt) DHL Packstation
    "account_no": "",  # (opt) DHL Postfiliale
}

ShipmentOrder = {
    "customs": {
        "invoice_no": "",
        "description": "",  # description for shipment
        "place_of_commital": "",  # Locaton the shipment is handed over to DHL
    },
    "positions": [],  # list of ShipmentOrderPosition
}

ShipmentOrderPosition = {
    "name": "",  # product name
    "amount": 0,
    "price": 0,
    "weight": 0.0,  # weight of single unit
    "weight_unit": "kg",  # unit; possible: kg, g
    "weight_total": 0.0,  # (opt) amount + weight
    "customs": {
        # c	ISO-Code (ISO 3166-2) of country the goods were manufactured
        "country_code_origin": "",
        # Customs tariff number of the unit / position. If the service PDDP is used, customsTariffNumber is required.
        "customs_tariff_number": "",
    },
}


def get_schema(schema_obj):
    """
    Conevert schema to string and back so python cannot refere to old values
    """
    return json.loads(json.dumps(schema_obj))
