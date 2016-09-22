import pandas as pd

execfile("load_banki.py")
execfile("load_banki_revoked.py")


# Takes banki dataset and banki's revoked dataset and merges them.
def merge_banki_revoked (banki, revoked):

    merged = banki.merge(revoked, how='left', on='lic_num')

    merged['period'] = pd.to_datetime(merged['period'])
    merged['revoc_date'] = pd.to_datetime(merged['revoc_date'])

    print "Calculating months..."
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

    merged = merged[cols]

    print "Writing merged set with months to file..."

    #merged.to_csv("../csv/banki_complete.csv", index=False)

    print "Returning..."

    return merged    

def merge_cbr_banki(cbr, banki):

    
    merged = banki.merge(cbr, how='left', on='lic_num')
