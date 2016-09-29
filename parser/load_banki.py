import pandas as pd
import numpy as np
import datetime as dt
from sys import stdout
import os
import pdb
import signal

ERASE_LINE = '\x1b[2K'
RETURN = '\r' + ERASE_LINE

# Global 90 second timeout for read_csv from banki. See handler below.
TIMEOUT = 90

execfile("dictionaries.py")

def timeout_handler(signum, frame):
	raise Exception('\n' + str(TIMEOUT) + ' second timeout reached. Continuing...')

# Updates or redownloads banki indicator and revocation datasets.
# Calculates months. Merges with CBR.
# returns complete DataFrame.
def load_banki(update = False, redownload = False):

    if update:
        print 'Updating...'
        banki    = update_banki()
        revoked  = load_banki_revoked(update=True)
        complete = complete_banki(banki, revoked)
    elif redownload:
        print 'Redownloading...'
        banki    = redownload_banki()
        revoked  = load_banki_revoked(redownload=True)
        complete = complete_banki(banki, revoked)
    else:
        complete = pd.read_csv('../csv/banki_complete.csv', index_col=False)
        complete['period'] = pd.to_datetime(complete['period'])
    
    #cbr = pd.read_csv('../csv/cbr_standards_complete.csv', index_col=False)
    #cbr['period'] = pd.to_datetime(cbr['period'])
    #cbr.drop(['N1','N2','N3'], axis = 1, inplace=True)
    
    #final = complete.merge(cbr, how='outer', on=['lic_num', 'period', 'months'])
    
    return complete

# Download a set of indicator observations for a given month for all banks.
# Clean, and add meta to remember indicator and observation dates.
# param ind Indicator to download, the banki-defined ID.
# param year Year to download.
# param month Month to download.
# returns DataFrame
def download_ind_from_date(ind, year, month):

    now = dt.datetime.now()

    # Skip downloads for future dates.
    if year == now.year and month > now.month:
        return None
    
    # We're iterating downwards in time, where month and year
    # are ending dates, not starting. If the ending date is January, then
    # starting date is December last year.
    if month == 1:
        start_month = 12
        start_year = year - 1
    else:
        start_month = month - 1
        start_year = year

    # Convert to strings:
    month       = str(month)
    year        = str(year)
    start_month = str(start_month)
    start_year  = str(start_year)

    # Create date strings for banki request.
    time_end = year + "-" + month + "-01"
    time_start = start_year + "-" + start_month + "-01"

    url = "http://www.banki.ru/banks/ratings/export.php?LANG=en&" + \
        "PROPERTY_ID=" + str(ind) + \
        "&search[type]=name&sort_param=rating&sort_order=ASC&REGION_ID=0&" + \
        "date1=" + time_end + \
        "&date2=" + time_start + \
        "&IS_SHOW_GROUP=0&IS_SHOW_LIABILITIES=0"

    stdout.write(RETURN)
    stdout.write( '\rDownloading ' + get_ind(ind) + ', ' + time_end[0:-3])
    stdout.flush()
    
    # Download banki table.
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(TIMEOUT)
    try:
		df = pd.read_csv(url, delimiter=";", skiprows=3, error_bad_lines=False, warn_bad_lines=True)
    except Exception, e:
    	df = pd.DataFrame()
    	print e

	signal.alarm(0) # Cancel signal alarm

    # Cleanup data if it exists.
    if not df.empty:
        
        nine_cols = ['rating','rating_change','bank_name','lic_num',
            'region','ind_val','ind_start','change','perc_change']
        
        eight_cols = ['rating_change','bank_name','lic_num','region',
            'ind_val','ind_start','perc_change','empty']
        
        # Rename and drop columns for 9 or 8 tables.
        if len(df.columns) == 9:
            df.columns = nine_cols
            df.drop(['rating', 'change'], axis=1, inplace=True)
        else:
            df.columns = eight_cols
            df.drop('empty', axis=1, inplace=True)
    
        # Drop shared columns
        df.drop(['bank_name', 'region','rating_change', 'ind_start','perc_change'],
            axis = 1, inplace = True)
        
        # Convert indicator value to a number by first removing the
        # white spaces and replacing the comma decimal with the point decimal.
        df['ind_val'] = df['ind_val'].str.replace(' ', '').str.replace(',', '.')
        df['ind_val'] = pd.to_numeric(df['ind_val'])
        
        # Remember important details about this dataset, such as
        # the indicator and date.
        df['ind']    = pd.Series(get_ind(ind), index=df.index)
        df['period'] = pd.Series(time_end, index=df.index)
        df['period'] = pd.to_datetime(df['period'])
    else:
        df = None
    
    return df
    
# Make banki wide or banki tall using pd.pivot_table
# param df Generally, new DataFrame on export, banki.csv on import.
# param wide_or_tall
    # -> 'wide' to spread indicators over columns
    # -> 'tall' to gather indicators into rows
def pivot_banki(df, wide_or_tall=None):

    if wide_or_tall == 'wide':
        df = pd.pivot_table(df, index=['lic_num', 'period'],
            columns='ind', values='ind_val')
        df.reset_index(inplace=True)
    
    if wide_or_tall == 'tall':
        df = pd.melt(df,id_vars=['lic_num','period'],
            value_vars = list(df.columns[2:]),
            var_name = 'ind', value_name = 'ind_val')
        df['period'] = pd.to_datetime(df['period'])
        
    return df
    
# Redownload banki from scratch, using the indicators
# defined in dictionaries.py. Writes to banki.csv.
# returns DataFrame
def redownload_banki():

    now = dt.datetime.now()
    ind_codes = ind_dict_banki_ru()['ind_num'] # Defined in dictionaries.py
    final = pd.DataFrame()
    
    for ind in ind_codes:
        for year in range(now.year, 2007, -1):
            for month in range(12, 0, -1):
                tmp = download_ind_from_date(ind, year, month)
                # If tmp is None, then skip.
                if type(tmp) == pd.DataFrame:
                    final = final.append(tmp)

    final = export_banki(final)
    
    return final
    
# Update banki using local banki.csv. Writes to banki.csv.
# returns DataFrame
def update_banki():

    ind_codes = ind_dict_banki_ru()['ind_num'] #  Defined in dictionaries.py
    banki = pd.read_csv('../csv/banki.csv', index_col=False)
    
    # Revert wide banki to tall, so we can append and compare it
    # with the temporary tables we download from banki.ru
    banki = pivot_banki(banki, wide_or_tall='tall')
    
    # Here, the year/month for loops are refactored to the function,
    # help_iterdate_update() so we can break from downlading
    # an indicator once we see duplicates.
    for ind in ind_codes:
        final = help_iterdate_update(ind, banki)
    
    final = export_banki(final)
    
    return final

# Helps update_banki. Starts at the current date, moving backwards.
# Only downloads up to one set of duplicates, then moves on
# to the next indicator.
# param ind Indicator to download
# param banki Local banki.csv.
# returns DataFrame
def help_iterdate_update(ind, banki):

    now = dt.datetime.now()
    
    for year in range(now.year, 2007, -1):
        for month in range(12, 0, -1):
            tmp = download_ind_from_date(ind, year, month)
            if type(tmp) == pd.DataFrame:
                banki = banki.append(tmp)
                dups = banki.duplicated(['lic_num','period','ind'], keep=False)
                if any(dups):
                    banki.drop_duplicates(['lic_num','period','ind'],inplace=True)
                    return banki

# Takes final banki download, pivots, sorts, writes to file.
# param final Final banki download.
# returns DataFrame
def export_banki(final):
    
    final = pivot_banki(final, wide_or_tall='wide')
    final.sort_values(['lic_num', 'period'],
        ascending=[True, False], inplace=True) 
    
    print 'Writing banki.csv...'
    final.to_csv('../csv/banki.csv', index=False)
    
    return final

# banki.ru records the dates of license revocations in webpage-separated
# html tables. One webpage has 50 records. When the page index becomes
# greater than the actual number of pages, instead of showing an empty
# table, it returns to Page 1, but the index keeps incrementing.
# Highly inconvenient.
#
# Instead, in order to detect when we've reached the end of banki's
# dataset, we'll keep downloading until we find the first duplicate.
# If a csv already exists, then we'll check it first, then check
# banki's most recent records.

# param update If banki_revoked.csv exists then it will
#              fetch updates from banki.ru
# param redownload Download banki.ru's full dataset again.
# returns Pandas Dataframe of banki.ru's license revocations. Writes to csv.
def load_banki_revoked(update=False, redownload=False):

    print "Loading banki.ru's license revocations dataset."
    
    br_file = "../csv/banki_revoked.csv"

    # If the user wants to redownload then redownload.
    # If the file doesn't exist, then we'll have to redownload anyway.
    if redownload:
        banki_revoked = pd.DataFrame()
    # If the file exists, and the user doesn't want to update it,
    #   then read the csv and return it as a pandas DataFrame.
    # If they want to update it, then set banki_revoked to local dataset,
    #   and read banki.ru, stopping as soon as there are duplicates.
    elif update:
        print "Updating..."
        banki_revoked = pd.read_csv(br_file, index_col=False)
        banki_revoked['revoc_date'] = pd.to_datetime(banki_revoked['revoc_date']) 
    else:
        return pd.read_csv(br_file)

    i = 1
    while True:
        sys.stdout.flush()
        sys.stdout.write("\rReading Pages... " + str(i))
        url = 'http://www.banki.ru/banks/memory/?PAGEN_1=' + str(i)
        
        # The content we want is in [2] of the returned web thingy.
        tmp = pd.read_html(url)[2]
        
        # Rename columns
        tmp.columns = ['idx', 'bank', 'lic_num', 'cause', 'revoc_date', 'region']
        tmp.drop(['idx', 'bank', 'region', 'cause'], axis=1, inplace=True)
        tmp['revoc_date'] = pd.to_datetime(tmp['revoc_date'])
        
        # Remove rows whose license numbers have "-" + character.
        if tmp['lic_num'].dtype == 'object':
            tmp = tmp[~tmp.lic_num.str.contains("-")]
        tmp['lic_num'] = tmp['lic_num'].astype(int)
        banki_revoked = banki_revoked.append(tmp)
        
        # As soon as we find a duplicate, break.
        d = banki_revoked.duplicated(['lic_num', 'revoc_date'])
        if any(d): break
        i += 1

    print 'Cleaning...'
    # Actually remove duplicates.
    banki_revoked.drop_duplicates(['lic_num', 'revoc_date'],
                                  keep = False, inplace = True)

    banki_revoked.reset_index(inplace=True, drop=True)
    banki_revoked.sort_values(['revoc_date', 'lic_num'],
                              ascending=[False,True], inplace=True)

    print "Writing to file..."
    banki_revoked.to_csv("../csv/banki_revoked.csv", index=False)

    print "Returning dataset."
    return banki_revoked
    
# Takes banki dataset and banki's revoked dataset and merges them.
# param banki Indicator dataset
# param revoked License revocation dataset
# Writes to banki_complete.csv
# returns DataFrame
def complete_banki(banki, revoked):

	print 'Completing banki...'

	merged = banki.merge(revoked, how='left', on='lic_num')

	merged['period'] = pd.to_datetime(merged['period'])
	merged['revoc_date'] = pd.to_datetime(merged['revoc_date'])

	print '    Calculating months...'
	for row in merged.itertuples():
		if pd.notnull(row[-1]):
			merged = merged.set_value(row[0], 'months',
				12 * (row[-1].year - row[2].year) +
				(row[-1].month - row[2].month))
		else:
			merged = merged.set_value(row[0], 'months', 9000)

	for row in merged.itertuples():
		if row[-1] > 24 and row[-1] < 9000:
			merged = merged.set_value(row[0], 'months', 1000)


	merged.drop('revoc_date', axis=1, inplace=True)

	# Moves 'months' from last column to the third column.
	cols = merged.columns.tolist()
	cols = cols[0:2] + cols[-1:] + cols[2:-1]

	complete = merged[cols]

	print '    Merging with local CBR file...'

	cbr = pd.read_csv('../csv/cbr_standards_complete.csv', index_col=False)
	cbr['period'] = pd.to_datetime(cbr['period'])
	cbr.drop(['N1','N2','N3'], axis = 1, inplace=True)

	complete = complete.merge(cbr, how='outer', on=['lic_num', 'period', 'months'])
	complete.to_csv('../csv/banki_complete.csv', index=False)

	print '    Returning...'

	return complete
