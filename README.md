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
