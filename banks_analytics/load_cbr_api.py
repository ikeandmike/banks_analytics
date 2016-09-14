from suds.client import Client
from suds.xsd.doctor import ImportDoctor, Import
import pandas as pd
import sys


def load_crb_standards(license_num, date):
    # loads values of standards (aka normativs) which are binding on russian banks
    # license_num -- int value
    # date -- string 'yyyy-mm-ddT00:00:00+03:00'
    #    e.g. July, 1 2016 --> '2016-07-01T00:00:00+03:00'
    # this data is available for the fist days of each month
    # returns pandas data frame with values of standards for chosen bank & date
    url = 'http://www.cbr.ru/CreditInfoWebServ/CreditOrgInfo.asmx?WSDL'
    imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
    imp.filter.add('http://web.cbr.ru/')
    imp = Import('http://www.w3.org/2001/XMLSchema', location='http://www.w3.org/2001/XMLSchema.xsd')
    imp.filter.add('http://web.cbr.ru/')
    doctor = ImportDoctor(imp)

    client = Client(url, doctor=doctor)
    tmp = client.service.Data135FormFull(license_num, date)
    norms = tmp.diffgram.F135DATA.F135_3
    df = pd.DataFrame()
    for i in range(len(norms)):
        ind_name = norms[i].C3
        try:
            ind_value = norms[i].V3
        except AttributeError:
            ind_value = None
        df_tmp = pd.DataFrame({'Indicator_name': [ind_name], 'Indicator_value': [ind_value]})
        df = df.append(df_tmp, ignore_index = True)

    return df



