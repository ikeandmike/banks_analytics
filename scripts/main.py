import numpy as np
import os; import sys
sys.path.append('../bank_analytics')
from load_data import * 
from dictionaries import *



ind_name = 'loans'
ind_num = ind_num_by_name(ind_name, ind_dict_banki_ru())
loans = parse_banki_ru(ind_num = ind_num, date_begin = '2016-08-01')

print loans[0]
print len(loans)

