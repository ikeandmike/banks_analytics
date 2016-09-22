import pandas as pd
import datetime as dt
from decimal import *
import os

## TODO: Make it a function, add updating feature.

execfile("../banks_analytics/load_cbr_api.py")
banki = pd.read_csv("../csv/banki_complete.csv")


if os.path.isfile("/Users/jabortell/Desktop/cbr_tmp.csv"):
    cbr = pd.read_csv("/Users/jabortell/Desktop/cbr_tmp.csv", encoding='windows-1251', index_col=False)
    tmp_lic_nums = set(cbr['lic_num'])
else:
    tmp_lic_nums = []

now = dt.datetime.now()
cbr = pd.DataFrame()
years = range(2011, now.year + 1)
months = range(1, 13)
lic_nums = set(banki['lic_num'])
size = len(lic_nums)

n = 1
print "Downloading CBR Standards..."
for l in lic_nums:
    if l in tmp_lic_nums:
        n += 1
        break
    for i in years:
        for j in months:
            if i == now.year and j == now.month+1: break
            if j < 10: j = '0' + str(j)
            cbr_date = str(i) + '-' + str(j) + '-01T00:00:00+03:00'
            sys.stdout.flush()
            sys.stdout.write("\rBank: " + str(l) + ", Period: " + cbr_date[0:-18] + ", " + str(round(Decimal(n)/Decimal(size),3)) + "%")
            try:
                tmp = load_crb_standards(l, cbr_date)
                tmp['Indicator_value'] = pd.to_numeric(tmp['Indicator_value'])
                tmp['period'] = pd.Series(cbr_date, index = tmp.index)
                tmp['period'] = pd.to_datetime(tmp['period'])
                tmp['lic_num'] = pd.Series(l, index = tmp.index)
                tmp = pd.pivot_table(tmp, index=['lic_num','period'], columns='Indicator_name', values='Indicator_value')
                cbr = cbr.append(tmp)
            except AttributeError:
                tmp = None
            except Exception as e:
                print str(e)
                pass
    cbr.to_csv('~/Desktop/cbr_tmp.csv', encoding='windows-1251')
    n += 1
        
cbr.reset_index(inplace=True)
cbr.columns = ['lic_num','period','N1', 'N1_0', 'N1_1','N1_2','N1_3','N10_1','N12','N15',
    'N15_1','N16', 'N16_1', 'N16_2', 'N17', 'N18', 'N19', 'N2','N3','N4','N7','N9_1', 'T1', 'T2']

cbr.dropna(axis=0, how='all',subset=cbr.columns[2:],inplace=True)

cbr.to_csv("../csv/cbr_standards.csv", index=False)




