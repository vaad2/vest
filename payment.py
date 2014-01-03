from copy import deepcopy
from urllib import urlencode


class VTPayment(object):
    def pay_data(self, **kwargs):
        pass

    def pay_confirm(self, **kwargs):
        pass

    def pay_result(self, **kwargs):
        pass


# MrchLogin=sMerchantLogin&
# OutSum=nOutSum&
# InvId=nInvId&
# Desc=sInvDesc&
# SignatureValue=sSignatureValue
# IncCurrLabel=sIncCurrLabel&
# Culture=sCulture

class VTRobokassa(VTPayment):
    reserved = [
        'MerchantLogin', 'OutSum', 'InvId',
        'Desc', 'SignatureValue', 'IncCurrLabel', 'Culture',
        'MerchantPass1', 'MerchantPass2'
    ]

    def __init__(self, **kwargs):
        self.MerchantLogin = kwargs['MerchantLogin']
        self.MerchantPass1 = kwargs['MerchantPass1']
        self.MerchantPass2 = kwargs.get('MerchantPass2', '')

        self.url = 'http://test.robokassa.ru/Index.aspx' if kwargs.get(
            'TestMode') else 'https://auth.robokassa.ru/Merchant/Index.aspx'


    def crc(self, str_data):
        import hashlib

        md5 = hashlib.md5()
        md5.update(str_data)

        return md5.hexdigest()

    def params_pack(self, **kwargs):
        ex_params = []
        dc_params = {}

        for key, val in kwargs.iteritems():
            if key.startswith('shp'):
                ex_params.append('%s=%s' % (key, val))
                dc_params[key] = val

        if len(ex_params):
            ex_params.sort()

        return ex_params, dc_params

    def _signature_get(self, password, **kwargs):
        if 'MerchantLogin' in kwargs:
            str_sig = '%s:%s:%s:%s' % (kwargs['MerchantLogin'], kwargs['OutSum'], kwargs['InvId'], password)
        else:
            str_sig = '%s:%s:%s' % (kwargs['OutSum'], kwargs['InvId'], password)

        ex_params, dc_params = self.params_pack(**kwargs)
        if len(ex_params):
            str_sig = '%s:%s' % (str_sig, ':'.join(ex_params))

        return str_sig, dc_params


    def pay_data(self, **kwargs):
        kwargs['OutSum'] = '%.2f' % float(kwargs['OutSum'])
        str_sig, params = self._signature_get(self.MerchantPass1, MerchantLogin=self.MerchantLogin, **kwargs)
        params.update({'MrchLogin': self.MerchantLogin, 'OutSum': kwargs['OutSum'],
                       'InvId': kwargs['InvId'],
                       'Desc': kwargs.get('Desc', ''), 'Culture': kwargs.get('Culture', ''),
                       'SignatureValue': self.crc(str_sig)
        })

        return '%s?%s' % (self.url, urlencode(params))

    def pay_confirm(self, **kwargs):
        crc = kwargs['SignatureValue'].upper()
        str_sig, params = self._signature_get(self.MerchantPass2, **kwargs)

        return crc == self.crc(str_sig).upper()

    def pay_result(self, **kwargs):
        crc = kwargs['SignatureValue'].upper()
        str_sig, params = self._signature_get(self.MerchantPass1, **kwargs)

        return crc == self.crc(str_sig).upper()

