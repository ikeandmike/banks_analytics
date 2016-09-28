import sys

# dictionary of indicators for banki.ru
def ind_dict_banki_ru():
    return {'ind_num':[10,   # [0] net_assets
                       30,   # [1] net_profit
                       25,   # [2] equity_form123
                       20,   # [3] equity_form134
                       40,   # [4] loans
                       50,   # [5] overdue_loans
                       60,   # [6] individuals_deposits
                       70,   # [7] securities
                       1000, # [8] return_on_net_assets
                       1100, # [9] return_on_equity
                       1200, # [10] overdue_loans_share
                       1300, # [11] reserve_to_loans
                       1400, # [12] mortaged_property_to_loans
                       1500, # [13] foreign_currency_operations_to_net_assets
                       1550, # [14] foreign_currency_operations_rub
                       1600, # [15] N1
                       1700, # [16] N2
                       1800,
                       100],# [17] N3
            'ind_name':['net_assets',            # [0] 10
                        'net_profit',            # [1] 30
                        'equity_form123',        # [2] 25
                        'equity_form134',        # [3] 20
                        'loans',                 # [4] 40
                        'overdue_loans',         # [5] 50
                        'individuals_deposits',  # [6] 60
                        'securities',            # [7] 70
                        'return_on_net_assets',  # [8] 1000
                        'return_on_equity',      # [9] 1100
                        'overdue_loans_share',   # [10] 1200
                        'reserve_to_loans',      # [11] 1300
                        'mortaged_property_to_loans', # [12] 1400
                        'foreign_currency_operations_to_net_assets', # [13] 1500
                        'foreign_currency_operations_rub',           # [14] 1550
                        'N1',  # [15] 1600
                        'N2',  # [16] 1700
                        'N3',
                        'net_assets_carrying']} # [17] 1800

# param key 'ind_num' or 'ind_name'
def get_ind(inds):

    if type(inds) is not list: inds = [inds]

    result = []
    for i in inds:
        if type(i) is str:
            key = "ind_name"
            find = "ind_num"
        if type(i) is int:
            key = "ind_num"
            find = "ind_name"
        try:
            pos = ind_dict_banki_ru()[key].index(i)
        except ValueError:
            print "No indicator " + str(i)
            return None
        result.append(ind_dict_banki_ru()[find][pos])

    if len(result) == 1: result = result[0]

    return result

# Ranges for ratios. Ranges are dummy values right now.
# Ratios with no lower or upper bound will be assigned
# the min or max size of int, respectively.
def ratio_dict():
    return {'ind_name':['net_assets',            # [0] 
                        'net_profit',            # [1] 
                        'equity_form123',        # [2] 
                        'equity_form134',        # [3] 
                        'loans',                 # [4]
                        'overdue_loans',         # [5]
                        'individuals_deposits',  # [6]
                        'securities',            # [7]
                        'return_on_net_assets',  # [8]
                        'return_on_equity',      # [9]
                        'overdue_loans_share',   # [10]
                        'reserve_to_loans',      # [11]
                        'mortaged_property_to_loans', # [12]
                        'foreign_currency_operations_to_net_assets', # [13]
                        'foreign_currency_operations_rub',           # [14]
                        'N1',    # [15]
                        'N2',    # [16]
                        'N3',    # [17]
                        'N4',    # [18]
                        'N6',    # [19]
                        'N7',    # [20]
                        'N9_1',  # [21]
                        'N10_1', # [22]
                        'N12',   # [23]
                        'N1_0',  # [24]
                        'N1_1',  # [25]
                        'N1_2'], # [26]
            'ind_ratio':[None, # [0] net_assets
                         None, # [1] net_profit
                         None, # [2] equity_form123
                         None, # [3] equity_form134
                         None, # [4] loans
                         None, # [5] overdue_loans
                         None, # [6] individuals_deposits
                         None, # [7] securities
                         [0.015,sys.maxint], # [8] return_on_net_assets
                         [0.08,sys.maxint], # [9] return_on_equity
                         None, # [10] overdue_loans_share
                         None, # [11] reserve_to_loans
                         None, # [12] mortaged_property_to_loans
                         None, # [13] foreign_currency_operations_to_net_assets
                         None, # [14] foreign_currency_operations_rub
                         [0.1,sys.maxint],      # [15] N1
                         [0.15,sys.maxint],     # [16] N2
                         [0.5,sys.maxint],      # [17] N3
                         [-sys.maxint-1,1.2],   # [18] N4
                         [-sys.maxint-1,0.25],  # [19] N6
                         [-sys.maxint-1,8.0],   # [20] N7
                         [-sys.maxint-1,0.5],   # [21] N9_1
                         [-sys.maxint-1,0.03],  # [22] N10_1
                         [-sys.maxint-1,0.25],  # [23] N12
                         [0.08,sys.maxint],     # [24] N1_0
                         [0.045,sys.maxint],    # [25] N1_1
                         [0.06,sys.maxint]]}    # [26] N1_2
                
def get_ratio(inds):

    if type(inds) is not list: inds = [inds]

    result = []
    for i in inds:
        try:
            pos = ratio_dict()['ind_name'].index(i)
        except ValueError:
            print "No indicator " + str(i)
            return None
        result.append(ratio_dict()['ind_ratio'][pos])

    if len(result) == 1: result = result[0]

    return result
    
# CBR Standards
def cbr_standards():
    return ['N1', 'N1_0','N1_1','N1_2','N1_3','N10_1','N12','N15','N15_1','N16', 'N16_1','N16_2','N17','N18','N19','N2','N3','N4','N7','N9_1','T1','T2']
