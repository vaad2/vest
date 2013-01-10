# -*- coding: utf-8 -*-
from time import strftime, localtime
'''

def yml_categories():
    for category in ProductCatalog.commercial_cats_get():
        id = ProductCatalogYml.objects.get(product_catalog = category).id
        parentId = ''
        if category.parent_id:
            try:
                parentId = ProductCatalogYml.objects.get(product_catalog_id = category.parent_id).id
            except BaseException, e:
                parentId = ''
        yield { 'id' : id, 'parentId' : parentId, 'title' : category.title.encode('windows-1251') }

def yml_offers():
    currency_map = {
        'RUB' : 'RUR',
        'USD' : 'USD'
    }
    for category in ProductCatalogYml.objects.all():
        for product in mongo_get('product').find({'groups' : category.product_catalog_id }):
            if 'price_1' in product:

                yield { 'price' : product['price_1']['cenazaedinicu'],
                        'currencyId' : currency_map[product['price_1']['valyuta']],
                        'name' : product['naimenovanie']['znachenie'].encode('windows-1251'),
                        'categoryId' : category.id}



yml_gen = YMLGenerator()
info = { 'url' : 'http://partskeeper.ru',
         'name' : 'supershop',
         'company' : 'company',
         'platform' : 'vestlitems',
         'version' : '0.8',
         'agency': 'vestlite',
         'email' : 'vaad2@yandex.ru' }
currencies = [{
                  'id' : 'USD', 'rate' : 'CBRF',
                  'id' : 'EUR', 'rate' : 'CBRF'
            }]
'''
class YMLGenerator(object):
    #0
    def _write_header(self):
        self.file.write('''<?xml version="1.0" encoding="windows-1251"?><!DOCTYPE yml_catalog SYSTEM "shops.dtd">''')

    def _write(self, data):
        self.file.write(data)
    def _open_catalog(self):
        self._write(strftime('<yml_catalog date="%Y-%m-%d %H:%M">', localtime()))
    def _close_catalog(self):
        self._write('</yml_catalog>')
        #1
    def _open_shop(self, info):
        self._write('''
        <shop>
            <name>%(name)s</name>
            <company>%(company)s</company>
            <url>%(url)s</url>
            <platform>%(platform)s</platform>
            <version>%(version)s</version>
            <agency>%(agency)s</agency>
            <email>%(email)s</email>
        ''' % info)

    def _close_shop(self):
        self._write('</shop>')
        #2
    def _write_currency(self, currencies):
        str_currencies = '<currency id="RUR" rate="1"/>'
        for currency in currencies:
            str_currencies = '%s%s' % (str_currencies,
                                       '<currency id="%(id)s" rate="%(rate)s"/>' % currency)
        self._write('<currencies>%s</currencies>' % str_currencies)


    def _write_categories(self, categories):
        self._write('<categories>')
        for category in categories:
            self._write('<category id="%(id)s" parentId="%(parentId)s">%(title)s</category>' % category)
        self._write('</categories>')

    def _write_local_delivery_cost(self, local_delivery_cost):
        self._write('<local_delivery_cost>%s</local_delivery_cost>' % local_delivery_cost)

    def _write_if(self, key, item):
        if key in item:
            self._write('<%s>%s</%s>' % (key, item[key], key))

    def _write_offers(self, offers):
        self._write('<offers>')
        cnt = 0
        for offer in offers:
            cnt +=1

            #required
            self._write('<offer available="%(available)s" id="%(id)s">' % offer)
            self._write('<url>%(url)s</url>' % offer)
            self._write('<price>%s</price>' % offer['price'])
            self._write('<currencyId>%s</currencyId>' % offer['currencyId'])
            self._write('<categoryId>%s</categoryId>' % offer['categoryId'])
            self._write('<name>%s</name>' % offer['name'])
            #no required

            if 'picture' in offer and len(offer['picture']):
                if isinstance(offer['picture'], list):
                    for picture in offer['picture']:
                        self._write('<picture>%s</picture>', picture)
                else:
                    self._write_if('picture', offer)

            self._write_if('store', offer)
            self._write_if('pickup', offer)
            self._write_if('delivery', offer)
            self._write_if('local_delivery_cost', offer)
            self._write_if('vendor', offer)
            self._write_if('vendorCode', offer)
            self._write_if('description', offer)
            self._write_if('sales_notes', offer)
            self._write_if('manufacturer_warranty', offer)
            self._write_if('country_of_origin', offer)
            self._write_if('adult', offer)
            self._write_if('barcode', offer)
            if 'param' in offer:
                for key, val in offer['param'].iteritems():
                    if isinstance(val, dict):
                        self._write('<param name="%s" unit="%s">%s</param>' % (key, val['unit'], val['val']))
                    else:
                        self._write('<param name="%s">%s</param>' % (key, val))

                        #            self._write_ if('param', offer)
            self._write('</offer>')
        self._write('</offers>')


    def generate(self, path, **kwargs):
        try:
            self.file = open(path, 'w+')
            self._write_header()
            self._open_catalog()
            self._open_shop(kwargs['info'])
            self._write_currency(kwargs['currencies'])
            self._write_categories(kwargs['categories'])
            self._write_offers(kwargs['offers'])
            self._close_shop()
            self._close_catalog()
        except BaseException, e:
            from common.std import exception_details

            import logging
            log = logging.getLogger('file_logger')
            ed = unicode(exception_details())
            log.log(logging.DEBUG, ed)

            return { 'success' : False, 'error' : ed }
        finally:
            self.file.close()
        return { 'success' : True }

def yml_validate(file):
    from lxml import etree, objectify
    import os
    curr_dir = os.path.dirname(__file__)
    dtd = etree.DTD(open('%s/static/s1/shops.dtd' % curr_dir, 'rb'))
    tree = objectify.parse(open(file, 'rb'))
    return dtd.validate(tree)
