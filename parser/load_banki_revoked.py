import pandas as pd
import os
import sys

# banki.ru records the dates of license revocations in webpage-separated
# html tables. One webpage has about 50 records. When the page index becomes
# greater than the actual number of pages, instead of showing an empty
# table, it returns to Page 1, but the index keeps incrementing.
# Highly inconvenient.
#
# Instead, in order to detect when we've reached the end of banki's
# dataset, we'll keep downloading until we find the first duplicate.
# If a csv already exists, then we'll check it first, then check
# banki's most reset records.

# param update If banki_revoked.csv exists then it will
#              fetch updates from banki.ru
# param redownload Download banki.ru's full dataset again.
# returns Pandas Dataframe of banki.ru's license revocations. Writes to csv.
def load_banki_revoked(update=False, redownload=False):

    print "Loading banki.ru's license revocations dataset."
    
    br_file = "../csv/banki_revoked.csv" 
    br_exists = os.path.isfile(br_file)

    # If the user wants to redownload then redownload.
    # If the file doesn't exist, then we'll have to redownload anyway.
    if (not br_exists) or redownload:
        banki_revoked = pd.DataFrame()
        if not br_exists:
            print "No local dataset found. Re-downloading full dataset."
    # If the file exists, and the user doesn't want to update it,
    #   then read the csv and return it as a pandas DataFrame.
    # If they want to update it, then set banki_revoked to local dataset,
    #   and read banki.ru, stopping as soon as there are duplicates.
    elif br_exists:
        if not update:
            return pd.read_csv(br_file, encoding='windows-1251')
        else:
            print "Updating..."
            banki_revoked = pd.read_csv(br_file, index_col=0, encoding='windows-1251')
            banki_revoked['period'] = pd.to_datetime(banki_revoked['period'])

    i = 1
    while True:
        sys.stdout.write("\rReading Pages... " + str(i))
        sys.stdout.flush()
        url = 'http://www.banki.ru/banks/memory/?PAGEN_1=' + str(i)
        tmp = pd.read_html(url)[2]
        tmp.columns = ['idx', 'bank', 'lic_num', 'cause', 'period', 'region']
        tmp.drop(['idx', 'bank', 'region', 'cause'], axis=1, inplace=True)
        tmp['period'] = pd.to_datetime(tmp['period'])
        banki_revoked = banki_revoked.append(tmp)
        d = banki_revoked.duplicated(['lic_num', 'period'])
        if any(d): break
        i += 1

    print "Cleaning..."
    banki_revoked.drop_duplicates(['lic_num', 'period'],
                                  keep = False, inplace = True)

    banki_revoked.reset_index(inplace=True, drop=True)
    banki_revoked.sort_values(['period', 'lic_num'],
                              ascending=[False,True], inplace=True)

    print "Writing to file..."
    banki_revoked.to_csv("../csv/banki_revoked.csv", encoding='windows-1251')

    print "Returning dataset."
    return banki_revoked
