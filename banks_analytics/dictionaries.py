# dictionary of indicators for banki.ru
def ind_dict_banki_ru():
    return {'ind_num':[10,30,25,20,40,50,60,70,1000,1100,1200,1300,1400,1500,1550,1600,1700,1800],
            'ind_name':['net_assets', 'net_profit', 'equity_form123', 'equity_form134', 'loans', 'overdue_loans',
                        'individuals_deposits', 'securities', 'return_on_net_assets', 'return_on_equity', 'overdue_loans_share',
                        'reserve_to_loans', 'mortaged_property_to_loans', 'foreign_currency_operations_to_net_assets',  # ratios
                        'foreign_currency_operations_rub', 'N1', 'N2', 'N3']}


# finds indicator number by its name in dictionary
# Accepts list or single value.
def ind_num_by_name(ind_names):

    if type(ind_names) is not list: ind_names = [ind_names]
    
    codes = []
    for name in ind_names:
	try:
	    pos = ind_dict_banki_ru()['ind_name'].index(name)
	except ValueError:
            print "No indicator named " + name
	    return None
	codes.append(ind_dict_banki_ru()['ind_num'][pos])

    if len(codes) == 1: codes = codes[0]
    
    return codes
    
# finds indictor name by its number in dictionary
# Accepts list or single value of ints.
def ind_name_by_num(ind_nums):

    if type(ind_nums) is not list: ind_nums = [ind_nums]
        
    names = []
    for ind in ind_nums:
        try:
            pos = ind_dict_banki_ru()['ind_num'].index(ind)
        except ValueError:
            print "No indicator for number " + str(ind)
            return
        names.append(ind_dict_banki_ru()['ind_name'][pos])

    if len(names) == 1: names = names[0]
    
    return names
