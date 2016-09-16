import pandas as pd
import numpy as np
import datetime
import sys

execfile("../banks_analytics/dictionaries.py")

###############################################################################
## Download from banki.ru
###############################################################################

# Downloads banking indicators for all available datetimes on banki.ru
# param ind_codes A single code or an array of indicator codes. These
#   codes are defined by banki.ru
# returns Pandas DataFrame of dataset. Writes to csv.
def load_banki (ind_codes):

    # Hard-coded indicator codes which behave different than N1, N2, and N3
    exceptions = [1000, 1600, 1700, 1800]

    # This empty data frame will collect all the tables from banki.
    # In other words, we'll collect data from banki in temporary tables
    # and append them to the banki_final.
    banki_final = pd.DataFrame()

    # For each indicator, for every month of every year.
    for k in ind_codes:
        print ( "Downloading " + ind_name_by_num(k) + "..." )
        for i in range(2008, datetime.datetime.now().year + 1):
            for j in range(1,13):
                end_month = j + 1 # Recall that j is the iterating month.
                end_year = i      # i is the iterating year.
                                  # The only case when end_year does not
                                  # equal i will be when the months are
                                  # between December and January.
                                  
                if (j == 12):         # If the starting month is December
                    end_month = 1     # change the ending month to January,
                    end_year = i + 1  # and jump to the next year.
                
                # Our ending and starting dates.
                time_end = str(end_year) + "-" + str(end_month) + "-01"
                time_start = str(i) + "-" + str(j) + "-01"

                sys.stdout.write ("\r" + time_end)
                sys.stdout.flush()
                
                # Contructs the url which requests the download from banki.ru
                url = "http://www.banki.ru/banks/ratings/export.php?LANG=en&" + \
                    "PROPERTY_ID=" + str(k) + \
                    "&search[type]=name&sort_param=rating&sort_order=ASC&REGION_ID=0&" + \
                    "date1=" + time_end + \
                    "&date2=" + time_start + \
                    "&IS_SHOW_GROUP=0&IS_SHOW_LIABILITIES=0"
                    
                # Read the table from the url as csv into banki_table.
                banki_table = pd.read_csv(url, delimiter=";", \
                    skiprows=3, error_bad_lines=False, warn_bad_lines=True)
                
                # If nothing was downloaded, then skip to the next date.
                if banki_table.empty:
                    break
                    
                #banki_table.to_csv("/Users/jabortell/Desktop/test.csv")

                # Change names. Notice the 'empty' column. For some reason, banki's dataset has a one long empty column of NAs.
                if k not in exceptions:
                    banki_table.columns = ['rating', 'rating_change', 'bank_name','lic_num',
                                           'region', 'ind_end', 'ind_start', 'change', 'perc_change']
                    try:
                        banki_table.drop(['rating'])
                    except:
                        pass
                    try:
                        banki_table.drop(['change'])
                    except:
                        pass                   
                else:                       
                    banki_table.columns = ['rating_change', 'bank_name', 'lic_num', \
                        'region', 'ind_end', 'ind_start', 'perc_change', 'empty']
                    banki_table.drop('empty',axis=1, inplace=True)

                # Drop unimportant columns
                banki_table.drop(['rating_change', 'ind_start', 'perc_change'], axis = 1, inplace = True)
                
                # Clean data. For the end-of-the-month indicator value,
                # we'll convert it to a number by first removing the
                # white spaces and replacing the comma decimal
                # with the point decimal.
                banki_table['ind_end'] = banki_table['ind_end'].str.replace(' ', '').str.replace(',', '.')
                
                # Convert to numeric.
                banki_table['ind_end'] = pd.to_numeric(banki_table['ind_end'])
                
                # Remember important details about this dataset, such as
                # the indicator and date.
                banki_table['ind'] = pd.Series(ind_name_by_num(k), index = banki_table.index)
                banki_table['time_end'] = pd.Series(time_end, index = banki_table.index)
                banki_table['time_end'] = pd.to_datetime(banki_table['time_end'])
                
                banki_final = banki_final.append(banki_table)
                
            # End j (months)
        # End i (years)
    # End k (indicators)

    print "Download complete."

    # Clean environment
    #del banki_table, , ind_codes, end_month, end_year, i, j, k, time_end, time_start, url

    ###############################################################################
    ## Merge with local CBR summer data
    ############################################################################

    print "Preparing data..."

    # Indicators will now be column-wise.
    banki_wide = pd.pivot_table(banki_final,
        index=['time_end', 'lic_num'], columns='ind',values='ind_end')
        
    # The pivot_table created MultiIndex-style indices, but we need the table
    # to be flat, so we can join banki with cbr.
    banki_wide.reset_index(inplace=True)

    banki_wide['lic_num'] = banki_wide['lic_num'].astype(int)

    return banki_wide
####################################### STOP HERE FOR NOW ######################
    print "    Loading local CBR data..." 

    # Load in the summer CBR data.
    cbr = pd.read_csv("../csv/cbr_summer.csv")

    # Convert columns to proper formats
    cbr['time_end'] = pd.to_datetime(cbr['time_end'])
    cbr['lic_num'] = cbr['lic_num'].astype(int)

    print "    Merging..." 

    # Merge CBR with banki.
    cbr_banki = pd.merge(cbr, banki_wide, how="outer",
        on=['lic_num','time_end'])

    cbr_banki.sort_values(['lic_num','time_end'])

    # banki's N2 and N3 are in percent format but CBR's were not.
    cbr_banki['1700'] = cbr_banki['1700'] / 100
    cbr_banki['1800'] = cbr_banki['1800'] / 100

    print "    Copying missing values..."  

    # If CBR is missing any data, we'll copy it from banki.
    for row in cbr_banki.itertuples(name='row'):
        
        # If N1 (cbr) is empty, fill it with 1600 (banki)
        if pd.isnull(row[4]): cbr_banki = cbr_banki.set_value(row[0], 'N1', row[12])
        
        # If N2 (cbr) is empty, fill it with 1700 (banki)
        if pd.isnull(row[5]): cbr_banki = cbr_banki.set_value(row[0], 'N2', row[13])
        
        # If N3 (cbr) is empty, fill it with 1800 (banki)
        if pd.isnull(row[6]): cbr_banki = cbr_banki.set_value(row[0], 'N3', row[14])

    # Now that we've copied from banki, we can delete the banki columns.
    cbr_banki.drop(['1600','1700','1800'], axis=1, inplace=True)

    print "    Calculating months until revocations..." 

    max_dates = cbr_banki.groupby('lic_num').agg({'time_end' : np.max}).reset_index()

    cbr_banki = pd.merge(cbr_banki, max_dates, how="left", on='lic_num')

    for row in cbr_banki.itertuples(name='row'):
        cbr_banki = cbr_banki.set_value(row[0], 'months',
            12 * (row[-1].year - row[1].year) +
            (row[-1].month - row[1].month))

    print "    Writing to file."

    cbr_banki.to_csv("../csv/model_data_py.csv")

    print "Process complete."
