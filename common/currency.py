import lxml
from common.std import file_get_contents
from lxml import etree
SBR_URL = 'http://www.cbr.ru/scripts/XML_daily.asp'
def usd_rate_get(silent = True):
    rate = None
    try:
        rate = float(etree.fromstring(file_get_contents(SBR_URL)).find(u'Valute[@ID="R01235"]/Value').text.replace(',', '.'))
    except BaseException, e:
        if not silent:
            raise e
    return rate



def rates_get():
    return etree.fromstring(file_get_contents(SBR_URL)).findall(u'Valute')