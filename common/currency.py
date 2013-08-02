import lxml
from common.std import file_get_contents
from lxml import etree
SBR_URL = 'http://www.cbr.ru/scripts/XML_daily.asp'
CURRENCY_MAP = {
    'usd' : 'R01235',
    'kzt' : 'R01335',
    'uah' : 'R01720'
}


def rate_get(name, silemt=True):
    code = CURRENCY_MAP[name]
    rate = None
    try:
        rate = float(etree.fromstring(file_get_contents(SBR_URL)).find(u'Valute[@ID="%s"]/Value' % code).text.replace(',', '.'))
    except BaseException, e:
        if not silent:
            raise e
    return rate


def rates_get():
    return etree.fromstring(file_get_contents(SBR_URL)).findall(u'Valute')