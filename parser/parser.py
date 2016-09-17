import pandas as pd
import numpy as np
import datetime as dt
import argparse

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

print args.select

raise SystemExit(0)

execfile("../banks_analytics/dictionaries.py")
execfile("load_banki_revoked.py")
execfile("load_banki.py")
execfile("merge_banki_revoked.py")


banki = load_banki(update=args.update_banki, redownload=args.redownload_banki)
revoked = load_banki_revoked(update=args.update_revoked, redownload=args.redownload_revoked)

banki = merge_banki_revoked(banki, revoked)
banki.to_csv("../csv/model_data_" + str(dt.date.today()) + ".csv", index=False)

#execfile("banki_revoked.py")



#banki_revoked = load_banki_revoked(update=True)

# 1. Get banki revoked dataset.
# 2. Merge with banki data
# 3. Get cbr data
# 4. Merge with banki data
