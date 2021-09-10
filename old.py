# coding: utf-8
from flask import render_template_string
from app import app
import time, datetime, pytz

import urllib2, base64
from suds.client import Client
from suds.wsse import Security, UsernameToken
from suds.sax.element import Element
from suds.plugin import MessagePlugin

import textwrap

import logging

from app.malinlib import *

class DHL(MessagePlugin):
  def marshalled(self, context):
    #modify this line to reliably find the "Authentification" element
    context.envelope[1][0][0].setPrefix('Authentification')

  def sending(self, context):
    context.envelope = context.envelope.replace('EKP', 'Authentification:EKP')
    context.envelope = context.envelope.replace('partnerID', 'Authentification:partnerID')
    context.envelope = context.envelope.replace('accountNumber', 'Authentification:accountNumber')
    context.envelope = context.envelope.replace('name1', 'ns0:name1')
    context.envelope = context.envelope.replace('ns0:ns0:name1', 'ns0:name1')
    context.envelope = context.envelope.replace('shipmentNumber', 'Authentification:shipmentNumber')

    return context.envelope

class DHLAPIHandler(object):
  def __init__(self, shopsettings):
    self.response = None
    self.client = None
    self.version = None
    self.shopsettings = shopsettings
    self.msgContent = ''
    self.labelUrl = ''
    self.shipmentNumber = ''
    self.exportDocument = ''
    self.exportDocumentUrl = ''
    self.printOnlyIfCodeable = 1

    logging.basicConfig(level=logging.ERROR) #INFO
    logging.getLogger('suds.client').setLevel(logging.ERROR) #DEBUG
    logging.getLogger('suds.transport').setLevel(logging.ERROR) #DEBUG

    self.getSoapHeader()

  def getSoapHeader(self):
    urlWSDL = 'https://cig.dhl.de/cig-wsdls/com/dpdhl/wsdl/geschaeftskundenversand-api/3.0/geschaeftskundenversand-api-3.0.wsdl'
    #self.shopsettings.dhl_istest = True

    authUrl = 'https://cig.dhl.de/services/sandbox/soap'
    #self.shopsettings.dhl_authusername = 'jep01'
    #self.shopsettings.dhl_authpassword = 'pKy8WplDuA86byh-!SzZf8'

    if not self.shopsettings.dhl_istest:
      authUrl = 'https://cig.dhl.de/services/production/soap'
      #authUsername = 'magento_1'
      #authPassword = '2de26b775e59279464d1c2f8546432e62413372421c672db36eaacfc2f'

    #self.shopsettings.dhl_dhlusername = 'geschaeftskunden_api'
    #self.shopsettings.dhl_dhlpassword = 'Dhl_ep_test1'
    #self.shopsettings.dhl_dhlEKP = '5000000000'

    #if not isTest:
    #  dhlUsername = 'magentoweb'
    #  dhlPW = '1Magento!'
    #  dhlEKP = '5233743367'

    #headers =  {'login': self.shopsettings.dhl_authusername.lower(), 'password': self.shopsettings.dhl_authusername, 'location':authUrl, 'trace':1}

    self.client = Client(urlWSDL, username=self.shopsettings.dhl_authusername, password=self.shopsettings.dhl_authpassword, location=authUrl, plugins=[DHL()])
    ssnns = ('Authentification', 'http://dhl.de/webservice/cisbase')
    auth = Element('Authentification', ns=ssnns)
    usernameNS = Element('user', ns=ssnns).setText(self.shopsettings.dhl_dhlusername.lower())
    passwordNS = Element('signature', ns=ssnns).setText(self.shopsettings.dhl_dhlpassword)
    typeNS = Element('type', ns=ssnns).setText('0')
    auth.append(usernameNS)
    auth.append(passwordNS)
    #auth.append(typeNS)
    self.client.set_options(soapheaders=[auth], timeout=30)

    version = self.client.factory.create('ns1:Version')
    version.majorRelease = '3'
    version.minorRelease = '0'
    self.version = version

  def createShipment(self, sale):
    #app.logger.error(self.client)
    self.msgContent = ''
    self.labelUrl = ''
    self.shipmentNumber = ''
    self.response = None
    netWeight = 0

    # shipmentOrder
    shipmentOrder = self.client.factory.create('ShipmentOrderType')
    shipmentOrder.sequenceNumber = '01'

    ## shipmentDetails
    shipmentDetails = self.client.factory.create('ShipmentDetailsTypeType')
    #print shipmentDetails


    if sale.shippingaddress.country == 'DE':
      shipmentDetails.product = 'V01PAK'
      shipmentDetails.accountNumber = '52337433670101'
    else:
      shipmentDetails.product = 'V53WPAK'
      shipmentDetails.accountNumber = '52337433675301'

      if sale.shippingaddress.country not in ('BE','BG','CZ','DK','DE','EE','IE','EL','ES','FR','GR','HR','IT','CY','LV','LT','LU','HU','MT','NL','AT','PL','PT','RO','SI','SK','FI','SE'):
        #saleDocInvoice = sale.lastinvoice()
        #docCreateDate = sale.createdate.strftime('%Y-%m-%d')
        #if not saleDocInvoice:
        #  docCreateDate = saleDocInvoice.createdate.strftime('%Y-%m-%d')

        # check if we need a export document (only for not EU destination required)
        exportDoc = self.client.factory.create('ExportDocumentType')
        #exportDoc.InvoiceType = 'commercial'
        #exportDoc.invoiceDate = docCreateDate
        exportDoc.invoiceNumber = sale.no
        exportDoc.exportType = 'OTHER'
        exportDoc.exportTypeDescription = 'Fotobücher'.decode('utf8')
        exportDoc.placeOfCommital = self.shopsettings.dhl_shipper_city
        exportDoc.additionalFee = 0.0
        #exportDoc.CommodityCode = '4911990000'
        #exportDoc.TermsOfTrade = 'CPT'
        #exportDoc.Description = textwrap.wrap('Kleine Prints-Fotobücher fuer Kinder'.decode('utf8'), 30)[0]
        #exportDoc.CountryCodeOrigin = 'DE'
        #exportDoc.CustomsCurrency = 'EUR'
        #exportDoc.WithElectronicExportNtfctn = True
        #exportDoc.MRNNumber = sale.no

        countItems = 0
        valueItems = 0.0
        count = 0

        exportPositions = []

        sortedSaleItems = sorted(sale.saleitems, key=lambda x: x.subpricetotal, reverse=True)
        for item in sortedSaleItems:
          if 'Gutschein' not in item.sku.skuname and item.subpricetotal > 0 and count < 5:
            count = count + 1
            countItems = countItems + int(item.quantity)
            valueItems = valueItems + item.subpricetotal

            #exportPos = self.client.factory.create('ns0:ExportDocPosition')
            """
            exportPos.Description = 'Fotobuch' #item.sku.skuname
            exportPos.ISOCountryCodeOfOrigin = 'DE'
            exportPos.Amount = int(item.quantity)
            exportPos.NetWeightInKG = 0.3
            exportPos.GrossWeightInKG = 0.3
            exportPos.ValuePerPiece = item.itemprice
            exportPos.CommodityCode = '49119900'
            """

            description = item.sku.skuname
            if type(description) != unicode:
              description = description.decode('utf8')

            itemWeight = 0.3 * item.quantity
            exportPos = {
                'description' : textwrap.wrap(description, 256)[0]
                ,'countryCodeOrigin' : 'DE'
                ,'customsTariffNumber' : '49119900'
                ,'amount' : int(item.quantity)
                ,'netWeightInKG' : 0.3
                ,'customsValue' : item.subpricetotal
                #,'GrossWeightInKG' : itemWeight
                #,'CommodityCode' : '49119900'
                #,'CustomsCurrency' : 'EUR'
            }
            exportPositions.append(exportPos)

            netWeight = netWeight + itemWeight

        exportDoc.ExportDocPosition = exportPositions
        #print exportPositions
        #exportDoc.Amount = int(countItems)
        #exportDoc.CustomsValue = valueItems
        #exportDoc.InvoiceTypeSpecified = 1
        #exportDoc.ExportTypeSpecified = 1;
        shipmentOrder.Shipment.ExportDocument = exportDoc

    shipmentDetails.shipmentDate = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    shipmentDetails.customerReference = sale.no

    ### Attendance
    #attendance = self.client.factory.create('ns0:Attendance')
    #attendance.partnerID = '01'
    #shipmentDetails.Attendance = attendance


    if netWeight == 0.0:
      for item in sale.saleitems:
        itemWeight = 0.3 * item.quantity
        netWeight = netWeight + itemWeight

      if netWeight == 0.0:
        netWeight = 1.0

    ### shipmentItem
    shipmentItem = self.client.factory.create('ShipmentItemType')
    shipmentItem.weightInKG = netWeight
    #shipmentItem.lengthInCM' : 50
    #shipmentItem.WidthInCM' : 50
    #shipmentItem.HeightInCM = 50
    #shipmentItem.PackageType' : 'PK'
    shipmentDetails.ShipmentItem = shipmentItem

    shipmentOrder.Shipment.ShipmentDetails = shipmentDetails

    # shipper
    shipper = self.client.factory.create('ShipperType')
    shipper.Name.name1 = self.shopsettings.dhl_shipper_company
    shipper.Name.name2= self.shopsettings.dhl_shipper_company2

    shipper.Address.streetName = self.shopsettings.dhl_shipper_street
    shipper.Address.streetNumber = self.shopsettings.dhl_shipper_streetnumber
    shipper.Address.zip =  self.shopsettings.dhl_shipper_zip
    shipper.Address.city = self.shopsettings.dhl_shipper_city
    if self.shopsettings.dhl_shipper_countryiso == 'UK':
      shipper.Address.Origin.countryISOCode = 'GB'
    else:
      shipper.Address.Origin.countryISOCode = self.shopsettings.dhl_shipper_countryiso

    #shipper.Address.careOfName = self.shopsettings.dhl_shipper_careofname

    shipper.Communication.email = self.shopsettings.dhl_shipper_email
    shipper.Communication.phone = self.shopsettings.dhl_shipper_phone
    #shipper.Communication.internet = self.shopsettings.dhl_shipper_internet
    shipper.Communication.contactPerson = self.shopsettings.dhl_shipper_contactperson

    shipmentOrder.Shipment.Shipper = shipper

    receiver = self.client.factory.create('ReceiverType')
    receiver.name1 = sale.shippingaddress.firstname + ' ' + sale.shippingaddress.surname
    #if sale.shippingaddress.company != '':
    #  receiver.Company.Company = {
    #                              'name1' : sale.shippingaddress.company
    #                            }
    #
    #  receiver.Communication.contactPerson = sale.shippingaddress.firstname + ' ' + sale.shippingaddress.surname
    #else:
    #  receiver.Company.Person = {
    #                              'salutation' : sale.shippingaddress.title
    #                              ,'firstname' : sale.shippingaddress.firstname
    #                              ,'lastname' : sale.shippingaddress.surname
    #                            }

    receiver.Communication.contactPerson = sale.shippingaddress.firstname + ' ' + sale.shippingaddress.surname
    receiver.Communication.email = sale.customer.email
    if sale.shippingaddress.country != 'DE' and sale.shippingaddress.phone == '':
      receiver.Communication.phone = self.shopsettings.dhl_shipper_phone
    else:
      receiver.Communication.phone = sale.shippingaddress.phone

    if sale.shippingaddress.packstation != '' and sale.shippingaddress.packstation != '0' and sale.shippingaddress.country == 'DE':
      #packstation = self.client.factory.create('PackstationType')
      #packstation.PackstationNumber = sale.shippingaddress.streetnumber
      #packstation.PostNumber = sale.shippingaddress.packstation
      #packstation.Zip = sale.shippingaddress.zip
      #packstation.City = sale.shippingaddress.city
      receiver.Packstation = {
                                 'packstationNumber' : sale.shippingaddress.streetnumber
                                  ,'postNumber' : sale.shippingaddress.packstation
                                  ,'zip' : sale.shippingaddress.zip
                                  ,'city' : sale.shippingaddress.city
                                }
    elif sale.shippingaddress.dhlaccount != '' and sale.shippingaddress.dhlaccount != '0' and sale.shippingaddress.country == 'DE':
      receiver.Postfiliale = {
          'postfilialNumber' : sale.shippingaddress.streetnumber
          ,'postNumber' : sale.shippingaddress.dhlaccount
          ,'zip' : sale.shippingaddress.zip
          ,'city' : sale.shippingaddress.city
      }
    else:
      recAddress = self.client.factory.create('ns0:ReceiverNativeAddressType')
      recAddress.name2 = sale.shippingaddress.company
      recAddress.streetName = sale.shippingaddress.street1
      recAddress.streetNumber = sale.shippingaddress.streetnumber
      recAddress.zip = sale.shippingaddress.zip

      recAddress.city = sale.shippingaddress.city
      if sale.shippingaddress.country == 'UK':
        recAddress.Origin.countryISOCode = 'GB'
      else:
        recAddress.Origin.countryISOCode = sale.shippingaddress.country

      #recAddress.addressAddition = (sale.shippingaddress.district + ' ' + sale.shippingaddress.careOfName + ' ' + sale.shippingaddress.floorNumber + ' ' + sale.shippingaddress.roomNumber + ' ' + sale.shippingaddress.note).strip()[:35]
      recAddress.name3 = (sale.shippingaddress.district + ' ' + sale.shippingaddress.careOfName + ' ' + sale.shippingaddress.floorNumber + ' ' + sale.shippingaddress.roomNumber + ' ' + sale.shippingaddress.note).strip()[:50]

      receiver.Address = recAddress

    shipmentOrder.Shipment.Receiver = receiver

    if self.printOnlyIfCodeable == 1:
      shipmentOrder.PrintOnlyIfCodeable = 1

    #shipmentOrder.labelResponseType  = 'URL'
    #labelResponseType = self.client.factory.create('LabelResponseType')
    #print(self.client)
    #print(labelResponseType)

    self.response = self.client.service.createShipmentOrder(
        self.version, shipmentOrder, 'URL')
    #print 'Response', self.response
    app.logger.debug(self.response)
    if self.response.Status.statusCode == 0:
      self.msgContent = 'Done'
      self.labelUrl = self.response.CreationState[0].LabelData.labelUrl
      self.shipmentNumber = self.response.CreationState[0].shipmentNumber
    else:
      self.msgContent = 'StatusCode: ' + str(self.response.Status.statusCode)
      self.msgContent = self.msgContent + ', StatusMessage: ' + ''.join(self.response.Status.statusMessage) + '_; '
      #if self.response.CreationState
      #for state in self.response.CreationState:
      #  for msg in state.StatusMessage:
      #    self.msgContent = self.msgContent + msg + '; '

      return False


    return True

  def deleteShipment(self, shipmentNumber):
    #print self.client
    app.logger.debug(self.client)
    shipmNumber = self.client.factory.create('ns0:ShipmentNumberType')
    shipmNumber = shipmentNumber

    self.response = self.client.service.deleteShipmentOrder(self.version, shipmNumber)
    #print self.response

    app.logger.debug(self.response)
    if self.response.Status.statusCode == 0:
      self.msgContent = 'Done'
      return True

    self.msgContent = 'StatusCode: ' + str(self.response.Status.statusCode)
    self.msgContent = self.msgContent + ', StatusMessage: ' + ''.join(self.response.Status.statusMessage) + '_; '
    #for state in self.response.DeletionState:
    #  for msg in state.Status:
    #    print msg
    #    self.msgContent = self.msgContent + msg + '; '

    return False


  def getExportDocument(self, shipmentNumber):
    #print self.client

    shipmNumber = self.client.factory.create('ns0:ShipmentNumberType')
    shipmNumber = shipmentNumber

    self.response = self.client.service.getExportDoc(self.version, shipmNumber)
    #print self.response
    app.logger.debug(self.response)
    if self.response.Status.statusCode == 0:
      self.msgContent = 'Done'
      if hasattr(self.response.ExportDocData[0], 'ExportDocPDFData'):
        self.exportDocument = self.response.ExportDocData[0].ExportDocPDFData
      elif self.response.ExportDocData[0].exportDocURL:
        # download exportDocURL
        self.exportDocumentUrl = self.response.ExportDocData[0].exportDocURL
      else:
        self.msgContent = 'ERROR: could not get export document content.'
        return False

      return True
    else:
      self.msgContent = 'StatusCode: ' + str(self.response.Status.statusCode)
      self.msgContent = self.msgContent + ', StatusMessage: ' + self.response.Status.statusMessage + '_; '
      #for state in self.response.DeletionState:
      #  for msg in state.Status:
      #    print msg
      #    self.msgContent = self.msgContent + msg + '; '

      return False

    return False
