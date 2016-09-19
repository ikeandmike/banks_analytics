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
                       1800],# [17] N3
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
                        'N3']} # [17] 1800

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
                        'N1',  # [15]
                        'N2',  # [16]
                        'N3',  # [17]
                        'N4',  # [18]
                        'N6',  # [19]
                        'N7',  # [20]
                        'N9_1', # [21]
                        'N10_1', # [22]
                        'N12'] # [23]
            'ind_ratio':[[0, 1], # [0] net_assets
                         [0, 1], # [1] net_profit
                         [0, 1], # [2] equity_form123
                         [0, 1], # [3] equity_form134
                         [0, 1], # [4] loans
                         [0, 1], # [5] overdue_loans
                         [0, 1], # [6] individuals_deposits
                         [0, 1], # [7] securities
                         [0, 1], # [8] return_on_net_assets
                         [0, sys.maxint], # [9] return_on_equity
                         [0, 1], # [10] overdue_loans_share
                         [0, 1], # [11] reserve_to_loans
                         [0, 1], # [12] mortaged_property_to_loans
                         [0, 1], # [13] foreign_currency_operations_to_net_assets
                         [0, 1], # [14] foreign_currency_operations_rub
                         [0.1,sys.maxint], # [15] N1
                         [0.15,sys.maxint], # [16] N2
                         [0.5,sys.maxint]  # [17] N3
                         [-sys.maxint-1,1.2]   # [18] N4
                         [-sys.maxint-1,0.25]   # [19] N6
                         [-sys.maxint-1,8.0]   # [20] N7
                         [-sys.maxint-1,0.5]   # [21] N9_1
                         [-sys.maxint-1,0.03]   # [22] N10_1
                         [-sys.maxint-1,0.25]]} # [23] N12
                
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
    
