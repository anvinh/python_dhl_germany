import os
import logging
from datetime import datetime
import textwrap

import zeep
import base64
import requests
from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.


logger = logging.getLogger(__file__)


EU_COUNTRY_CODES = [
    "DE",
    "BE",
    "BG",
    "CZ",
    "DK",
    "DE",
    "EE",
    "IE",
    "EL",
    "ES",
    "FR",
    "GR",
    "HR",
    "IT",
    "CY",
    "LV",
    "LT",
    "LU",
    "HU",
    "MT",
    "NL",
    "AT",
    "PL",
    "PT",
    "RO",
    "SI",
    "SK",
    "FI",
    "SE",
]


class DHL:
    __version__ = "0.1.0"
    __dhl_version__ = "3.3.0"

    def __init__(
        self, auth_user, auth_password, api_user, api_password, is_test=False
    ):
        self.auth_user = auth_user
        self.auth_password = auth_password
        self.api_user = api_user
        self.api_password = api_password
        self.is_test = is_test
        self.client = self._get_client()
        self.version = self._get_version()

    def _get_wsdl_file(self):
        if self.is_test:
            return os.path.join(
                os.path.dirname(__file__), "wsdl/3.3.0/test.wsdl"
            )
        return os.path.join(
            os.path.dirname(__file__), "wsdl/3.3.0/production.wsdl"
        )

    def _get_auth_header(self):
        auth_type = zeep.xsd.Element(
            "{http://dhl.de/webservice/cisbase}Authentification",
            zeep.xsd.ComplexType(
                [
                    zeep.xsd.Element(
                        "{http://dhl.de/webservice/cisbase}user",
                        zeep.xsd.String(),
                    ),
                    zeep.xsd.Element(
                        "{http://dhl.de/webservice/cisbase}signature",
                        zeep.xsd.String(),
                    ),
                ]
            ),
        )
        return auth_type(user=self.api_user, signature=self.api_password)

    def _get_version(self):
        return {"majorRelease": "3", "minorRelease": "1"}

    def _get_client(self):
        session = Session()
        session.auth = HTTPBasicAuth(self.auth_user, self.auth_password)
        client = zeep.Client(
            wsdl=self._get_wsdl_file(),
            transport=zeep.transports.Transport(session=session, timeout=30),
        )
        client.set_default_soapheaders([self._get_auth_header()])
        return client

    def _get_shipper(self, shipper):
        shipper_name = self.client.get_type("ns0:NameType")(
            name1=shipper["name"], name2=shipper.get("name2")
        )
        address = self.client.get_type("ns0:NativeAddressTypeNew")(
            streetName=shipper["street"],
            streetNumber=shipper["street_number"],
            zip=shipper["zip"],
            city=shipper["city"],
            Origin=self.client.get_type("ns0:CountryType")(
                countryISOCode=shipper["country_code"]
            ),
        )
        communication = self.client.get_type("ns0:CommunicationType")(
            phone=shipper["phone"],
            email=shipper["email"],
            contactPerson=shipper["contact_person"],
        )

        return self.client.get_type("ns1:ShipperType")(
            Name=shipper_name, Address=address, Communication=communication
        )

    def _get_receiver(self, receiver, fallback_phone=""):
        phone = receiver.get("phone")
        if phone == "":
            phone = fallback_phone

        dhl_receiver = self.client.get_type("ns1:ReceiverType")(
            name1=receiver["name"],
            Communication=self.client.get_type("ns0:CommunicationType")(
                phone=phone,
                email=receiver.get("email"),
            ),
        )

        if (
            receiver.get("packing_station")
            and receiver.get("packing_station") != "0"
        ):
            dhl_receiver.Packstation = self.client.get_type(
                "ns0:PackStationType"
            )(
                packstationNumber=receiver["street_number"],
                postNumber=receiver["packing_station"],
                zip=receiver["zip"],
                city=receiver["city"],
            )
        elif receiver.get("account_no") and receiver.get("account_no") != "0":
            receiver.Postfiliale = self.client.get_type(
                "ns0:PostfilialeTypeNoCountry"
            )(
                postfilialNumber=receiver["street_number"],
                postNumber=receiver["account_no"],
                zip=receiver["zip"],
                city=receiver["city"],
            )
        else:
            dhl_receiver.Address = self.client.get_type(
                "ns0:ReceiverNativeAddressType"
            )(
                name2=receiver.get("name2"),
                streetName=receiver["street"],
                streetNumber=receiver["street_number"],
                zip=receiver["zip"],
                city=receiver["city"],
                Origin=self.client.get_type("ns0:CountryType")(
                    countryISOCode=receiver["country_code"]
                ),

                name3=" ".join(
                    [
                        receiver.get("district", "") if receiver.get(
                            "district", "") else "",
                        receiver.get("careOfName", "") if receiver.get(
                            "careOfName", "") else "",
                        receiver.get("floorNumber", "") if receiver.get(
                            "floorNumber", "") else "",
                        receiver.get("roomNumber", "") if receiver.get(
                            "roomNumber", "") else "",
                        receiver.get("note", "") if receiver.get(
                            "note", "") else "",
                    ]
                ).strip()[:50],
            )

        return dhl_receiver

    def _get_shipment_details(
        self, dhl_product, dhl_account_number, order_id, weight_total
    ):
        return self.client.get_type("ns1:ShipmentDetailsTypeType")(
            product=dhl_product,
            accountNumber=dhl_account_number,
            shipmentDate=datetime.now().strftime("%Y-%m-%d"),
            customerReference=order_id,
            ShipmentItem=self.client.get_type("ns1:ShipmentItemTypeType")(
                weightInKG=weight_total
            ),
        )

    def _get_export_document(self, order):
        logger.debug("create export document", order)
        if "customs" not in order:
            logger.error(
                "ERROR: could not find customs information on order", order
            )
            raise Exception(
                "ERROR: could not find customs information on order", order
            )

        export_positions = []
        for position in order["positions"]:
            if "customs" not in position:
                logger.error(
                    "ERROR: could not find customs information on position",
                    position,
                )
                raise Exception(
                    "ERROR: could not find customs information on position",
                    position,
                )
            export_positions.append(
                {
                    "description": textwrap.shorten(
                        position["name"], width=256, placeholder="..."
                    ),
                    "countryCodeOrigin": position["customs"][
                        "country_code_origin"
                    ],
                    "customsTariffNumber": position["customs"][
                        "customs_tariff_number"
                    ],
                    "amount": position["amount"],
                    "customsValue": position["price"],
                    "netWeightInKG": position["weight_unit"] / 1000.0,
                }
            )

        return self.client.get_type("ns1:ExportDocumentType")(
            invoiceNumber=order["customs"]["invoice_no"],
            exportType="OTHER",
            exportTypeDescription=order["customs"]["description"],
            placeOfCommital=order["customs"]["place_of_commital"],
            ExportDocPosition=export_positions,
        )

    def get_version(self):
        return self.client.service.getVersion(majorRelease=3, minorRelease=1)

    def get_label(self, shipment_number):
        return self.client.service.getLabel(
            Version=self.version, shipmentNumber=shipment_number
        )

    def get_label_from_url(self, url):
        response = requests.get(url)
        return base64.b64encode(response.content)

    def create_shipment_order(
        self,
        order_id: str,
        shipper: dict,
        receiver: dict,
        weight_total: float,
        dhl_product: str,
        dhl_account_number: str,
        label_type="URL",
        label_format="910-300-600",
        force_print=False,
        order_to_ship=None,
    ):
        try:
            shipment_order_type = self.client.get_type("ns1:ShipmentOrderType")

            shipment = {
                "ShipmentDetails": self._get_shipment_details(
                    dhl_product, dhl_account_number, order_id, weight_total
                ),
                "Shipper": self._get_shipper(shipper),
                "Receiver": self._get_receiver(receiver, shipper["phone"]),
            }

            # create export documents if receiver country is not in the EU
            if receiver["country_code"] not in EU_COUNTRY_CODES:
                logger.debug(
                    "create export document for not EU",
                    receiver["country_code"],
                )
                shipment["ExportDocument"] = self._get_export_document(
                    order_to_ship
                )

            shipment_order = shipment_order_type(
                sequenceNumber=order_id,
                Shipment=shipment,
                PrintOnlyIfCodeable=force_print,
            )

            return self.client.service.createShipmentOrder(
                Version=self.version,
                ShipmentOrder=shipment_order,
                labelResponseType=label_type,
                labelFormat=label_format,
            )
        except Exception as ex:
            logger.error("could not create shipment", ex)
            raise Exception("could not create shipment", ex)
