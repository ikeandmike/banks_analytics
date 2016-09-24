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

# Initialize Argument Parser object.
parser = argparse.ArgumentParser()

# Banki indicator dataset argument group.
# One can only update or redownload, but not both.
group = parser.add_mutually_exclusive_group()

group.add_argument(
	"-u",
	"--update",
	action="store_true",
	help="Update banki.ru indicator and revocation datasets."
	)
group.add_argument(
	"-r",
	"--redownload",
	action="store_true",
	help="Redownload banki.ru indicator and revocation dataset."
	)

# User can pass column names to the script
parser.add_argument(
    "-s",
    "--select",
    metavar="COLUMNS",
    nargs='*',
    help="Select columns from indicator dataset to use in model. \
    To receive binary indicators (ie. is indicator in acceptable range) \
    add a bang after the indicator (ie. 'N1!'). To calculate values between \
    indicators, use Lisp notation: (/ (+ net_assets net_profit) loans)"
    )

args = parser.parse_args()

##################################
## Load Local Scripts, File Paths,
## and Variables
##################################

execfile("dictionaries.py")
execfile("load_banki.py")
execfile("load_banki_revoked.py")
execfile("merge_banki_revoked.py")

# Local datasets:
banki          = "../csv/banki.csv"           # Banki indicators, no months.
banki_revoked  = "../csv/banki_revoked.csv"   # Banki revocation dates.
banki_complete = "../csv/banki_complete.csv"  # Banki inds. and months.

banki_ind_names = ind_dict_banki_ru()['ind_name'] # Banki indicator names

##################################

##################################
## Function Definitions
##################################

def parse_select(orig_select):

    select = orig_select[:] # Make a copy of the original selection.
    
    singular_cols = []   # When parsing the command line, keep these columns.
    range_cols    = []   # Columns are true/false if the Indicator is in range.
    equation_cols = []   # These are equations between columsn
    
    # Iterate throughe each item asked for selection from the command-line.
    for i in select:
        # If i is immediately found in the list of indicators,
        # then is a singularly requested column.
        if i in banki_ind_names:
            singular_cols.append(i)
        # Now, look for operators like ! and /
        else:
            # if string.index doesn't find "!", it returns an Exception.
            try:
                string.index(i, '!')
                ind_name = string.split(i, '!')[0]
                range_cols.append(ind_name)
            except ValueError:
                equation_cols.append(i)
                
        
    return [singular_cols, range_cols, equation_cols]
# End parse_select(..)

# Puts all the helper functions together to add string equations passed
# from the command line to the model_data DataFrame.
# param df The DataFrame to which to add the results of the equations.
# param eq_list The string equations passed from the command line.
def add_eqs(df, eq_list):

    # Use banki_complete which has all the indicators.
    banki = pd.read_csv("../csv/banki_complete.csv", index_col=False)

    # For each equation passed from the command line...
    for eq in eq_list:
        # Get the recursive form of the equation.
        recursive_eq_str = eq_helper(eq)
        # Evaluate the column.
        col = df_eval_equations(banki, recursive_eq_str)
        # Create a syntatically appropriate column name.
        eq_str_col_name = eq.replace(' ','_')
        # Add it to the DataFrame
        df.insert(len(df.columns), eq_str_col_name, col)

    return df

# Parses equation string into recursive list for df_eavl_equations.
# Example:
#   in: '(/ (+ net_assets net_profit) loans)'
#  out: ['(+ net_assets net_profit)', '(/ (+ net_assets net_profit) loans)']
def eq_helper(eq):
    
    parens = [] # Keeps list of index location of opening parentheses.
    parts  = [] # Collects parts of equation string.
    
    # Iterate thourgh equation string, remembering positions of open parens,
    # and collectins substrings between open and closed parens.
    for c in range(0, len(eq)):
        if eq[c] == '(' : parens.append(c)
        if eq[c] == ')' : parts.append(eq[parens.pop() : c+1])

    return parts

# Recursive function which takes output from eq_helper
# to calculate operations on columns.
# param df The Pandas DataFrame which has all the source columns,
#    such as banki_complete.csv
# param sets The list returned from eq_helper.
# param tmp_col To calculate multiple operations, we save the result of one operation to a column, then operate on that temporary column to continue.
# Returns Pandas Series - The calculated column.
def df_eval_equations(df, sets, tmp_col=0):
    
    # Eventually, the final element of sets will be the Series.
    if type(sets) == pd.Series:
        return sets

    # Set the current working string to the first element of sets.
    this = sets[0]
    operator = this[1]            # Save the operator.
    operands = this[3:-1].split() # Get the operands.
    
    # The temporary result begins with the value of the first operand.
    tmp_result = df[operands[0]]
    
    # For all the operands...
    for op in range(1, len(operands)):

        # Set the column with which to operate.
        op_value = df[operands[op]]
    
        # Math.
        if operator == '/': tmp_result = tmp_result / op_value
        if operator == '*': tmp_result = tmp_result * op_value
        if operator == '+': tmp_result = tmp_result + op_value
        if operator == '-': tmp_result = tmp_result - op_value
        if operator == '^': tmp_result = tmp_result ** op_value

    # If sets > 1, then there are more operations to parse.
    if len(sets) > 1:
        # Make a temporary column.
        tmp_col += 1
        # Set the new temporary column to the value of the temp result.
        df[str(tmp_col)] = tmp_result
        # Change the final element of sets (the full equation string),
        # such that the current equation string is replaced by the
        # temporary column name we just created.
        # Example:
            # sets: [(+ N1 N2), (/ (+ N1 N2) loans)]
            #  -> : [(+ N1 N2), (/ 1 loans)]
        sets[-1] = sets[-1].replace(this, str(tmp_col))
        # Continue evaluting, removing the first element of sets.
        return df_eval_equations(df, sets[1:], tmp_col)
    # If sets has only one element left, then we have finished evaluting.
    else:
        # Make sets tmp_result, the final result.
        # When sets goes through the recursion, the type test will capture it,
        # and return the final result.
        sets = tmp_result
        return df_eval_equations(df, sets, tmp_col)

####################################


parsed_args = parse_select(args.select)

singular_cols  = parsed_args[0]
range_cols     = parsed_args[1]
equation_cols  = parsed_args[2] 

# Load indicator and revocation datasets.
if args.redownload:
    banki   = load_banki(redownload = True)
    revoked = load_banki_revoked(redownload = True)
    banki_complete = merge_banki_revoked(banki, revoked)
    
elif args.update:
    banki    = load_banki(update = True)
    revoked  = load_banki_revoked(update = True)
    banki_complete = merge_banki_revoked(banki, revoked)
else:
    banki_complete = pd.read_csv('../csv/banki_complete.csv', index_col=False)


# Add singular columns first.
model_data = banki_complete[['lic_num','period','months'] + singular_cols]

print model_data.head().to_string()

# Add ! columns:
for col in range_cols:
    r = get_ratio(col)
    
    new_col = col + '!'
    model_data[new_col] = banki_complete[col].apply(lambda x: r[0] <= x <= r[1] if pd.notnull(x) else None)

# Add equation columns:
model_data = add_eqs(model_data, equation_cols)

print "Writing to csv..."
model_data.to_csv("../csv/model_data.csv", index=False)

raise SystemExit(0)