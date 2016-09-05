# dictionary of indicators for banki.ru
def ind_dict_banki_ru():
    return {'ind_num':[10,30,25,20,40,50,60,70,1000,1100,1200,1300,1400,1500,1550,1600,1700,1800],
            'ind_name':['net_assets', 'net_profit', 'equity_form123', 'equity_form134', 'loans', 'overdue_loans',
                        'individuals_deposits', 'securities', 'return_on_net_assets', 'return_on_equity', 'overdue_loans_share',
                        'reserve_to_loans', 'mortaged_property_to_loans', 'foreign_currency_operations_to_net_assets',  # ratios
                        'foreign_currency_operations_rub', 'N1', 'N2', 'N3']}


# finds indicator number by its name in dictionary
def ind_num_by_name(ind_name, ind_dict):  
    try:
        pos = ind_dict['ind_name'].index(ind_name)
    except ValueError:
        return None
    return ind_dict['ind_num'][pos]
