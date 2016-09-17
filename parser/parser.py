import pandas as pd
from sys import stdout
import os
import numpy as np

###############################################################################
## Download from banki.ru
###############################################################################

#wk_dir = os.path.dirname(os.path.realpath('__file__'))

#os.chdir(wk_dir)

# 1600 is N1, 1700 is N2, 1800 is N3
ind_codes = ["1600", "1700", "1800"]

# We'll iterate through all date combinations.
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
years = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]

# This empty data frame will collect all the tables from banki.
# In other words, we'll collect data from banki in temporary tables
# and append them to the banki_final.
banki_final = pd.DataFrame()

# For each indicator, for every month of every year.
for k in ind_codes:
    print ( "Downloading indicator " + k + "..." )
    for i in years:
        for j in months:
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
            
            # Contructs the url which requests the download from banki.ru
            url = "http://www.banki.ru/banks/ratings/export.php?LANG=en&" + \
                "PROPERTY_ID=" + k + \
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
                
            # Change names. Notice the 'empty' column. For some reason, banki's dataset has a one long empty column of NAs.
            banki_table.columns = ['rating.change', 'bank.name', 'lic_num', \
                'region', 'ind_end', 'ind.start', 'perc.change', 'empty']

            # Drop unimportant columns
            banki_table.drop(['rating.change', 'ind.start', 'perc.change','empty'], axis = 1, inplace = True)
            
            # Clean data. For the end-of-the-month indicator value,
            # we'll convert it to a number by first removing the
            # white spaces and replacing the comma decimal
            # with the point decimal.
            banki_table['ind_end'] = banki_table['ind_end'].str.replace(' ', '').str.replace(',', '.')
            
            # Convert to numeric.
            banki_table['ind_end'] = pd.to_numeric(banki_table['ind_end'])
            
            # Remember important details about this dataset, such as
            # the indicator and date.
            banki_table['ind'] = pd.Series(k, index = banki_table.index)
            banki_table['time_end'] = pd.Series(time_end, index = banki_table.index)
            banki_table['time_end'] = pd.to_datetime(banki_table['time_end'])
            
            banki_final = banki_final.append(banki_table)
            
        # End j (months)
    # End i (years)
# End k (indicators)

print "Download complete."

# Clean environment
del banki_table, months, years, ind_codes, end_month, end_year, i, j, k, time_end, time_start, url

###############################################################################
## Merge with local CBR summer data
###############################################################################

print "Preparing data..."

# Indicators will now be column-wise.
banki_wide = pd.pivot_table(banki_final,
    index=['time_end', 'lic_num'], columns='ind',values='ind_end')
    
# The pivot_table created MultiIndex-style indices, but we need the table
# to be flat, so we can join banki with cbr.
banki_wide.reset_index(inplace=True)

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
