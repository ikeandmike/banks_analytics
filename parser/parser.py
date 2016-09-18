import pandas as pd
import numpy as np
import datetime as dt
import argparse
import string

pd.options.mode.chained_assignment = None

###############################
## Instantiate Script Arguments
###############################

parser = argparse.ArgumentParser()

# banki indicator dataset argument group
group_banki = parser.add_mutually_exclusive_group()
group_banki.add_argument("-ub", "--update-banki", action="store_true",
                   help="Update banki.ru indicator dataset.")
group_banki.add_argument("-rb", "--redownload-banki", action="store_true",
                   help="Redownload banki.ru indicator dataset.")

# banki revoked dataset argument group
group_revoked = parser.add_mutually_exclusive_group()
group_revoked.add_argument("-ur", "--update-revoked", action="store_true",
                           help="Update banki.ru revocation dataset.")
group_revoked.add_argument("-rr", "--redownload-revoked", action="store_true",
                           help="Redownload banki.ru revocation dataset.")

# User can pass column names to the script
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

new_cols = {}

select = args.select[:]

# If there were select-column arguments given,
# check if they are correctly named.
# But first check if they are a mathematical operation.

if not args.select == None:
    for i in args.select:
        if not (i in ind_dict_banki_ru()['ind_name']):
            # First check if it has a mathematical operation.
            try:
                string.index(i, "/")
                ops = string.split(i, "/")
                col_name = ops[0] + "_over_" + ops[1]
                new_cols[col_name] = ops
                select.remove(i)
                select.extend(ops)
            except ValueError:
                # If not, then it must be a badly formed name.
                print "No indicator named " + i + " in dictionary."
                print "Exiting..."
                raise SystemExit(0)
        
# If no columns were specified, get all the columns.
else:
    args.select = ind_dict_banki_ru()['ind_name']

# If there are no update or redownload requests, and the file exists,
# just read in the local file.
if not (args.update_banki or args.redownload_banki or args.update_revoked
        or args.redownload_revoked) and os.path.isfile("../csv/banki_complete.csv"):
    banki = pd.read_csv("../csv/banki_complete.csv", index_col=False)
# Otherwise, perform all updates and redownloads, merge, and calculate months.
else:
    # Load banki indicator dataset.
    banki = load_banki(update=args.update_banki,
                   redownload=args.redownload_banki)

    # Load banki license revocations dataset.
    revoked = load_banki_revoked(update=args.update_revoked,
                             redownload=args.redownload_revoked)

    # Merge the two.
    banki = merge_banki_revoked(banki, revoked)

model_data = banki[['lic_num', 'period', 'months'] + select]


# Add new columns and their evaluations to model_data.csv.
for col_name, ops in new_cols.iteritems():
    col_eval = model_data[ops[0]] / model_data[ops[1]]
    model_data.drop(ops, axis=1, inplace=True)
    model_data = model_data.assign(new_col = col_eval)
    model_data.rename(columns={'new_col':col_name}, inplace=True)

print "Writing model data to file..."

model_data.to_csv("../csv/model_data.csv", index=False)
