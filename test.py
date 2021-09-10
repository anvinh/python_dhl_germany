from dhl import DHL


auth_user = 'jep01'
auth_pw = 'PW'
dhl_user = '2222222222_01'
dhl_pw = 'pass'
dhl = DHL(auth_user, auth_pw, dhl_user, dhl_pw, is_test=True)

dhl_product = 'V62WP'
dhl_accountNumber = '22222222226201'
label_format = '100x70mm'
"""
dhl_product = 'V54EPAK'
dhl_accountNumber = '22222222225401'
label_format = '910-300-600'
dhl_product = 'V53WPAK'
dhl_accountNumber = '22222222225301'
label_format = '910-300-600'
"""


receiver = {
    'name': 'Johannes Eimer',
    'name2': 'JEP',
    'street': 'Kommodore-Johnsen-Boulevard',
    'street_number': '32',
    'zip': '28217',
    'city': 'Bremen',
    'country_code': 'DE',
    'phone': '015127078651',
    'email': 'johannes.eimer@jep-dev.com',
}

"""
receiver = {
    'name': 'Sylvia Wohlkinger',
    'name2': '',
    'street': 'Scheibenbergstrasse',
    'street_number': '52/2',
    'zip': '1180',
    'city': 'Wien',
    'country_code': 'AT',
    'phone': '00436507826962',
    'email': 'johannes.eimer@jep-dev.com',
}
"""

"""
receiver.get('district'),
receiver.get('careOfName'),
receiver.get('floorNumber'),
receiver.get('roomNumber'),
receiver.get('note')
"""

shipper = {
    'name': 'Johannes Eimer',
    'name2': 'JEP',
    'street': 'Kommodore-Johnsen-Boulevard',
    'street_number': '32',
    'zip': '28217',
    'city': 'Bremen',
    'country_code': 'DE',
    'phone': '015127078651',
    'email': 'info@jep-dev.com',
    'contact_person': 'Johannes Eimer',
}

#response = dhl.get_version()
#response = dhl.get_label('123556475867')
response = dhl.create_shipment_order(
    '1234',
    shipper,
    receiver,
    dhl_product, dhl_accountNumber,
    label_format=label_format
)
print(response)

#message = client.create_message(client.service, 'getLabel', Version=version, shipmentNumber='222201040006351235', _soapheaders=[auth])
#print(etree.tounicode(message, pretty_print=True))

#client.service.getLabel(Version=version, shipmentNumber='222201040006351235')
