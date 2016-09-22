#!/usr/bin/python

import pandas as pd
import numpy as np
import datetime as dt
import argparse
import string

pd.options.mode.chained_assignment = None

###############################
## Set Command Line Options
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
parser.add_argument("-s", "--select", metavar="COLUMNS", nargs='*',
                    help="Select columns from indicator dataset to use in model. To receive binary indicators (ie. is indicator in acceptable range) add a bang after the indicator (ie. 'N1!'). To receive ratios of indicators, specify with a slash (ie. 'N1/N2').")

parser.add_argument("-cbr", action="store_true",
                    help="Use CBR indicator dataset instead of banki.ru")

args = parser.parse_args()

###############################
## Load External Files
###############################

execfile("dictionaries.py")
execfile("load_banki.py")
execfile("load_banki_revoked.py")
execfile("merge_banki_revoked.py")

###############################
## Parse Command-Line Arguments
###############################

# Collect requests for indicator_I divided by indicator_j
new_ratios = {}
# Collect requests for "Is indicator within its range?"
new_bin_ranges = []

# If there were select-column arguments given,
# check if there is a request for division or range calculation.
if not args.select == None:
        # Helper list
        select = args.select[:]
        for i in args.select:
                if not (i in ind_dict_banki_ru()['ind_name'] or i in cbr_standards()):
                    # Check if there was passed an indicator_i/indicator_j
                    try:
                        # If there is no "/", string.index returns ValueError.
                        string.index(i, "/")
                        # Get the operands.
                        ops = string.split(i, "/")
                        
                        # Create new column name.
                        col_name = ops[0] + "_over_" + ops[1]
                        # Add to dictionary, {col_name : [op0, op1]}
                        new_ratios[col_name] = ops
                        # We're finished with this indicator equation.
                        select.remove(i)
                        # Add operands back as singular columns.
                        select.extend(ops)
                    except ValueError:
                        pass
                    # Check if it has ! for range operation.
                    try:
                        string.index(i, "!")
                        # Keep the column name and ignore the bang.
                        col_name = string.split(i, "!")[0]
                        r = get_ratio(col_name)
                        if r == None:
                        	print "No ratio for", col_name
                        	print "Exiting..."
                        	raise SystemExit(0)
                        new_bin_ranges.append(col_name)
                        select.remove(i)
                    except ValueError:
                        pass 
        
# If no columns were specified, get all the columns.
elif args.select == None and args.cbr:
        select = cbr_standards()
else:
    select = ind_dict_banki_ru()['ind_name']
    
###############################
## Load banki.ru datasets
###############################

# If there are no update or redownload requests, and the file exists,
# just read in the local file.

if args.cbr:
        if os.path.isfile("../csv/cbr_standards_complete.csv"):
                cbr = pd.read_csv("../csv/cbr_standards_complete.csv", index_col=False)
        else:
                print "Local CBR file not found. Exiting..."
                SystemExit(0)

if not (args.update_banki or args.redownload_banki or args.update_revoked
        or args.redownload_revoked) and os.path.isfile("../csv/banki_complete.csv"):
    # Read local csv
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


#############################################
## Post-Processing for Command-Line Arguments
#############################################

# Remove duplicates from select.

select = list(set(select))
columns = select + new_bin_ranges
columns = list(set(columns))

# Now we're ready to modify and cleanup the final dataset.
# Here, we add our singular columns and special requests to the table.

# TODO: Generalize this
if args.cbr:
        model_data = cbr[['lic_num', 'period', 'months'] + columns]
else:
        model_data = banki[['lic_num', 'period', 'months'] + columns]

# Add new column binary classifiers to model_data.csv.
for col in new_bin_ranges:
	# The ratios are defined in dictionaries.py
    r = get_ratio(col)

	# Add the new column with empty values. It keeps the ! in the name.
    model_data.insert(len(model_data.columns), col + "!", None)
    
    def in_range(x, lb, ub):
    	if pd.notnull(x):
    		return lb <= x <= ub
    
    # Calculate whether indicator-col is within its defined ratio.
    model_data[col + "!"] = model_data[col].apply(lambda x: r[0] <= x <= r[1] if pd.notnull(x) else None)
    
    if not col in select:
    	model_data.drop(col, axis=1, inplace=True)
    

seen = new_ratios.values()
# Add new column ratios and their evaluations to model_data
for col_name, ops in new_ratios.iteritems():
	# Evaluate a separate Series. Divide indicator_i by indicator_j
    
    col_eval = model_data[ops[0]] / model_data[ops[1]]
    
    # If the user specified that they wanted, for example, N2! as well as N2,
    # then make sure we remove it from ops, so we don't remove it
    # from model_data.
    for col in new_bin_ranges:
        if col in ops:
        	ops.remove(col)
	

    seen.remove(ops)
	
    for col in ops:
        # Flattens list [..]
    	if col in [item for sublist in seen for item in sublist]:
            ops.remove(col)
		
    # Remove operands if they weren't requested to stay.
    model_data.drop(ops, axis=1, inplace=True)
    # Add the new column to model_data
    model_data = model_data.assign(new_col = col_eval)
    # Rename the column to the actual name we defined earlier.
    model_data.rename(columns={'new_col':col_name}, inplace=True)
    
    model_data[col_name] = model_data[col_name].replace(np.inf, np.nan)

###############################
## Write to File
###############################      

print "Writing model data to file..."

model_data.to_csv("../csv/model_data.csv", index=False)
