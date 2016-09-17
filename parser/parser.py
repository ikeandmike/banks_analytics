import pandas as pd
import numpy as np
import datetime as dt
import argparse

###############################
## Instantiate Script Arguments
###############################

parser = argparse.ArgumentParser()
group_banki = parser.add_mutually_exclusive_group()
group_banki.add_argument("-ub", "--update-banki", action="store_true",
                   help="Update banki.ru indicator dataset.")
group_banki.add_argument("-rb", "--redownload-banki", action="store_true",
                   help="Redownload banki.ru indicator dataset.")

group_revoked = parser.add_mutually_exclusive_group()
group_revoked.add_argument("-ur", "--update-revoked", action="store_true",
                           help="Update banki.ru revocation dataset.")
group_revoked.add_argument("-rr", "--redownload-revoked", action="store_true",
                           help="Redownload banki.ru revocation dataset.")

parser.add_argument("-s", "--select", metavar="COLUMS", nargs='*',
                    help="Select columns from indicator dataset to use in model.")

args = parser.parse_args()

###############################
## Load External Files
###############################

execfile("../banks_analytics/dictionaries.py")
execfile("load_banki.py")
execfile("load_banki_revoked.py")
execfile("merge_banki_revoked.py")

###############################
## Create model data and export
###############################

if not (args.update_banki or args.redownload_banki or args.update_revoked
        or args.redownload_revoked) and os.path.isfile("../csv/banki_complete.csv"):
    banki = pd.read_csv("../csv/banki_complete.csv", index_col=False)
else:
    banki = load_banki(update=args.update_banki,
                   redownload=args.redownload_banki)

    revoked = load_banki_revoked(update=args.update_revoked,
                             redownload=args.redownload_revoked)

    banki = merge_banki_revoked(banki, revoked)

print args.select

model_data = banki[['lic_num', 'period', 'months'] + args.select]

print "Writing model data to file..."

model_data.to_csv("../csv/model_data.csv", index=False)
