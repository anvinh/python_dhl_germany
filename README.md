# python_dhl_germany

# New WSDL version
- Got to DHL Geschaeftskundenversand and download the zip:
https://entwickler.dhl.de/group/ep/wsapis/geschaeftskundenversand/current

- Create a new wsdl folder
- rename geschaeftskundenversand-api-x.x.x-wsdl to production.wsdl
- copy production.wsdl to test.wsdl
- open test.wsdl and patch
FROM: <soap:address location="https://cig.dhl.de/services/production/soap"/>
TO: <soap:address location="https://cig.dhl.de/services/sandbox/soap"/>

## install dev
virtualenv venv
venv/Scripts/activate
pip install -r requirements.txt -r requirements_dev.txt
pre-commit hook install: pre-commit install --hook-type pre-push

## build and deploy
python setup.py sdist bdist_wheel
s3pypi --bucket pypi.fourzero.one


# usage
dhl_client = DHL(
    "DHL_AUTH_USER", # test: DHL-Entwickler User / live: DHL App Name
    "DHL_AUTH_PASSWORD", # test: DHL-Entwickler PW / live: DHL App Token
    "API_USER", # test: 2222222222_01 / live: tenant user
    "API_PASSWORD", # test: pass / live: tenant pw
    is_test=True,
)

dhl_client.create_shipment_order(
    "ORDER_ID",
    shipper, # find example in integration test
    receiver, # find example in integration test
    6.0, # weight
    "V53WPAK", # dhl product
    "22222222225301", # dhl account number
    order_to_ship=order, # find example in integration test
)
