import pandas as pd
import numpy as np
import datetime as dt
import sys
import os

execfile("../banks_analytics/dictionaries.py")

###############################
## Prepare download process
###############################

# Downloads banking indicators for all available datetimes on banki.ru
# param ind_codes A single code or an array of indicator codes. These
#   codes are defined by banki.ru and held in dictionaries.py
# returns Pandas DataFrame of dataset. Writes to csv.
def load_banki (ind_codes = None, update=False, redownload=False):

    now = dt.datetime.now()

    print "Loading banki.ru's indicator dataset."

    br_file = "../csv/banki.csv"
    br_exists = os.path.isfile(br_file)

    # If the user wants to redownload then redownload.
    # If the file doesn't exist, then we'll have to redownload anyway.
    if (not br_exists) or redownload:
        banki_final = pd.DataFrame()
        # We'll start at the first year available.
        start_year_download = 2008
        start_month_download = 1
        # We'll download all indicators.
        ind_codes = ind_dict_banki_ru()['ind_num']
        if not br_exists:
            print "No local dataset found. Re-downloading full dataset."
    # If the file exists, and the user doesn't want to update it,
    #   then read the csv and return it as a pandas DataFrame.
    # If they want to update it, then set banki_final to local dataset,
    #   and read banki.ru, stopping as soon as there are duplicates.
    elif br_exists:
        if not update:
            return pd.read_csv(br_file)
        else:
            print "Updating..."
            banki_final = pd.read_csv(br_file)
            banki_final['period'] = pd.to_datetime(banki_final['period'])
            start_year_download = now.year
            if now.month == 1:
                start_month_download = 12
            else:
                start_month_download = now.month - 1
            if ind_codes == None:
                ind_codes = ind_dict_banki_ru()['ind_num']

###############################
## Download banki.ru dataset
###############################

    # For each indicator, for every month of every year.
    for k in ind_codes:
        sys.stdout.write ("\rDownloading " + get_ind(k) + "...\n")
        for i in range(start_year_download, now.year + 1):
            for j in range(start_month_download,13):
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
                sys.stdout.flush()
                sys.stdout.write("\rPeriod: " + time_end[0:-3])
                
                # Contructs the url which requests the download from banki.ru
                url = "http://www.banki.ru/banks/ratings/export.php?LANG=en&" + \
                    "PROPERTY_ID=" + str(k) + \
                    "&search[type]=name&sort_param=rating&sort_order=ASC&REGION_ID=0&" + \
                    "date1=" + time_end + \
                    "&date2=" + time_start + \
                    "&IS_SHOW_GROUP=0&IS_SHOW_LIABILITIES=0"
                    
                # Read the table from the url as csv into banki_table.
                banki_table = pd.read_csv(url, delimiter=";",
                    skiprows=3, error_bad_lines=False, warn_bad_lines=True)
                
                # If nothing was downloaded, then skip to the next date.
                if banki_table.empty:
                    break

                # Change names. For tables of column length 9, the names are fine.
                # But for 8-length, the names are wonky, and the last column is all NAs.
                if len(banki_table.columns) == 9:
                    banki_table.columns = ['rating', 'rating_change', 'bank_name','lic_num',
                                           'region', 'ind_val', 'ind_start', 'change', 'perc_change']
#                    try:
                    banki_table.drop(['rating'], axis=1, inplace=True) # TODO: is this doing anything?
#                    #except:
#                        pass
#                    try:
                    banki_table.drop(['change'], axis=1, inplace=True) # TODO: anything at all?
#                    except:
#                        pass
                else:                       
                    banki_table.columns = ['rating_change', 'bank_name', 'lic_num',
                                           'region', 'ind_val', 'ind_start', 'perc_change', 'empty']
                    banki_table.drop('empty', axis=1, inplace=True)

                # Drop unimportant columns
                banki_table.drop(['rating_change', 'ind_start', 'perc_change'], axis = 1, inplace = True)
                
                # For the end-of-the-month indicator value,
                # we'll convert it to a number by first removing the
                # white spaces and replacing the comma decimal
                # with the point decimal.
                banki_table['ind_val'] = banki_table['ind_val'].str.replace(' ', '').str.replace(',', '.')
                
                # Convert to numeric.
                banki_table['ind_val'] = pd.to_numeric(banki_table['ind_val'])
                
                # Remember important details about this dataset, such as
                # the indicator and date.
                banki_table['ind'] = pd.Series(get_ind(k),
                	index = banki_table.index)
                banki_table['period'] = pd.Series(time_end,
                	index = banki_table.index)
                banki_table['period'] = pd.to_datetime(banki_table['period'])

                # If we're updating, then all the columns already exist.
                # Merge instead of append.
                if update:
                    banki_final = pd.merge(banki_final, banki_table, how='left', on=['lic_num','period'])
                else:
                    banki_final = banki_final.append(banki_table)
                
            # End j (months)
        # End i (years)
    # End k (indicators)

    sys.stdout.write ("\nDownload complete.")

################################
## Prepare for Export and Return
################################

    print "Preparing..."

    # Indicators will now be column-wise.
    if not update:
        banki_wide = pd.pivot_table(banki_final,
            index=['lic_num', 'period'], columns='ind', values='ind_val')
    else:
        banki_wide = banki_final

    # The pivot_table created MultiIndex-style indices,
    # but we'd like the table to be flat.
    banki_wide.reset_index(inplace=True)

    banki_wide['lic_num'] = banki_wide['lic_num'].astype(int)
    banki_wide.drop_duplicates(['lic_num', 'period'], keep=False, inplace=True)
    banki_wide.sort_values(['lic_num', 'period'], ascending=[True, False], inplace=True)

    print "Writing to file..."
    banki_wide.to_csv("../csv/banki.csv", index=False)

    print "Process complete. Returning banki dataset."

    return banki_wide
