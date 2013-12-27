class VTPayment(object):
    def pay_data(self, **kwargs):
        pass

    def pay_confirm(self, **kwargs):
        pass

    def pay_result(self, **kwargs):
        pass

class VTRobokassa(VTPayment):
    def __init__(self, **kwargs):
        self.mrh_login = kwargs['mrh_login']
        self.mrh_pass1 = kwargs['mrh_pass1']
        self.mrh_pass2 = kwargs.get('mrh_pass2', '')
        self.ex_params = kwargs.get('ex_params', {})
        self.url = 'http://test.robokassa.ru/Index.aspx' if kwargs.get('test_mode') else 'https://auth.robokassa.ru/Merchant/Index.aspx'

    def crc(self, str_data):
        import hashlib

        md5 = hashlib.md5()
        md5.update(str_data)

        return md5.hexdigest()

    def params_pack(self, **kwargs):
        ex_params = []
        dc_params = {}

        dc_params.update(self.ex_params)
        dc_params.update(kwargs.get('ex_params', {}))

        for key, val in dc_params.iteritems():
            ex_params.append('shp_%s=%s' % (key, val))

        if len(ex_params):
            ex_params.sort()

        return ex_params

    #out_sum, inv_id
    def pay_data(self, **kwargs):
        str_data = '%s:%.2f:%s:%s' % (self.mrh_login, kwargs['out_sum'], kwargs['inv_id'], self.mrh_pass1)
        ex_params = self.params_pack(**kwargs)

        if len(ex_params):
            str_data = '%s:%s' % (str_data, ':'.join(ex_params))

        return self.url, {'MrchLogin': self.mrh_login, 'OutSum': '%.2f' % kwargs['out_sum'], 'InvId': kwargs['inv_id'],
                          'Desc': kwargs.get('desc', ''), 'SignatureValue': self.crc(str_data)

        }

    # MrchLogin=$mrh_login&".
    # "OutSum=$out_summ&InvId=$inv_id&Desc=$inv_desc&SignatureValue=$crc"
    #out_sum, inv_id
    def pay_confirm(self, **kwargs):
        crc = kwargs['crc'].upper()

        str_data = '%.2f:%s:%s' % (float(kwargs['out_sum']), kwargs['inv_id'], self.mrh_pass2)
        ex_params = self.params_pack(**kwargs)

        if len(ex_params):
            str_data = '%s:%s' % (str_data, ':'.join(ex_params))

        return crc == self.crc(str_data).upper()


    def pay_result(self, **kwargs):
        crc = kwargs['crc'].upper()

        str_data = '%.2f:%s:%s' % (float(kwargs['out_sum']), kwargs['inv_id'], self.mrh_pass1)
        ex_params = self.params_pack(**kwargs)

        if len(ex_params):
            str_data = '%s:%s' % (str_data, ':'.join(ex_params))

        return crc == self.crc(str_data).upper()




        # 3d915f8fe1fa7e6eac672076590538e3


# robo = VTRobokassa(mrh_login='mirbuketa', mrh_pass1='testtest1', mrh_pass2='testtest2',
#                    ex_params={'email': 'vaad2@ya.ru'})
# print robo.pay_data(out_sum=100.00, inv_id=1)
# print robo.pay_confirm(crc='22588FEC79367B8AE8A99C049531E3BC', out_sum=100.00, inv_id=1)