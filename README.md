# python_dhl_germany

# New WSDL version
- Got to DHL Geschaeftskundenversand and download the zip:
https://entwickler.dhl.de/group/ep/wsapis/geschaeftskundenversand/current

- Create a new wsdl folder
- rename geschaeftskundenversand-api-x.x.x-wsdl to production.wsdl
- copy production.wsdl to test.wsdl
- open test.wsdl and patch
  - FROM: <soap:address location="https://cig.dhl.de/services/production/soap"/>
  - TO: <soap:address location="https://cig.dhl.de/services/sandbox/soap"/>
- set new version in setup.py -> data_files (array)

## install dev
- create venv: python -m venv venv
- activate venv:
  - Windows: venv/Scripts/activate
  - Linux / Mac: source venv/bin/activate
- pip install -r requirements.txt -r requirements_dev.txt
- pre-commit hook install: pre-commit install --hook-type pre-push
- create .env file and add DHL_AUTH_USER + DHL_AUTH_PASSWORD variables

## build and deploy
- python setup.py sdist bdist_wheel
- s3pypi --bucket pypi.fourzero.one

# usage

create dhl client:
```
dhl_client = DHL(
    "DHL_AUTH_USER", # test: DHL-Entwickler User / live: DHL App Name
    "DHL_AUTH_PASSWORD", # test: DHL-Entwickler PW / live: DHL App Token
    "API_USER", # test: 2222222222_01 / live: Geschäftskunden-Portal system user name
    "API_PASSWORD", # test: pass / live: Geschäftskunden-Portal system user pw
    is_test=True,
)
```

create shipment order:
```
shipper = {
    "name": "Something Something GmbH",
    "name2": "",
    "street": "Teststraße",
    "street_number": "32",
    "zip": "22222",
    "city": "Bremen",
    "country_code": "DE",
    "phone": "040251090",
    "email": "test@test.com",
    "contact_person": "Test User",
}

receiver = {
    "name": "Test Tester",
    "name2": "TestCompany",
    "street": "Teststraße",
    "street_number": "12",
    "zip": "28217",
    "city": "Bremen",
    "country_code": "DE",
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

dhl_client.create_shipment_order(
    "ORDER_ID",
    shipper, # find example in integration test
    receiver, # find example in integration test
    6.0, # weight
    "V01PAK", # dhl product
    "22222222220101", # dhl account number
    order_to_ship=order, # find example in integration test
)
```
