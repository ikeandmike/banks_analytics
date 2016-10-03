#!/usr/bin/python

import pandas as pd
import numpy as np
import datetime as dt
import argparse
import string

pd.options.mode.chained_assignment = None
pd.set_option('mode.use_inf_as_null', True)

###############################
## Set Command Line Options
###############################

# Initialize Argument Parser object.
parser = argparse.ArgumentParser()

# Banki indicator dataset argument group.
# One can only update or redownload, but not both.
group_banki = parser.add_mutually_exclusive_group()

group_banki.add_argument(
	'-u',
	'--update',
	action='store_true',
	help='Update banki.ru indicator and revocation datasets.'
	)
group_banki.add_argument(
	'-r',
	'--redownload',
	action='store_true',
	help='Redownload banki.ru indicator and revocation dataset.'
	)
	
# Print indicators one can use for the model and exit.
parser.add_argument(
	'-i',
	'--indicators',
	action='store_true',
	help='Prints list of available indicators from banki.ru and CBR and exits.'
	)

# User can pass column names to the script
parser.add_argument(
    '-s',
    '--select',
    metavar='COLUMNS',
    nargs='*',
    help="Select columns from indicator dataset to use in model. \
    To receive binary indicators (ie. is indicator in acceptable range) \
    add a bang after the indicator (ie. 'N1!'). To calculate values between \
    indicators, use Lisp notation: '(/ (+ net_assets net_profit) loans)'"
    )

args = parser.parse_args()

##################################
## Load Local Scripts, File Paths,
## and Variables
##################################

execfile("dictionaries.py")
execfile("load_banki.py")

# Local datasets:
banki          = "../csv/banki.csv"           # Banki indicators, no months.
banki_revoked  = "../csv/banki_revoked.csv"   # Banki revocation dates.
banki_complete = "../csv/banki_complete.csv"  # Banki inds. and months.

# Banki indicator names and cbr hacked in there.
banki_ind_names = ind_dict_banki_ru()['ind_name'] + cbr_standards() 

if args.indicators:
	print 'Selectable indicators to run for the model:'
	for i in banki_ind_names:
		print i
	raise SystemExit(0)


##################################

##################################
## Function Definitions
##################################

# Take the column select argumens (from -s, --select), and put them
# into bins for further processing.
# param select The argument list from args.select
def parse_select(select):
    
    singular_cols = []   # Keep these basic columns.
    range_cols    = []   # Columns are true/false if the Indicator is in range.
    equation_cols = []   # These are equations between columns.
    
    # Iterate through each selected item from the command-line.
    for i in select:
        # If i is immediately found in the list of indicators,
        # then is a singular, basic column.
        if i in banki_ind_names:
            singular_cols.append(i)
        # Now, look for ! operator
        else:
			bangs = i.find('!')
			paren = i.find('(')
			if bangs != -1:
				ind_name = string.split(i, '!')[0]
				range_cols.append(ind_name)
			elif paren != -1:
				equation_cols.append(i)
			else:
				print i, 'is ivalid. Run `python parser.py -i` for full list of indicators.'
				raise SystemExit(0)

    return [singular_cols, range_cols, equation_cols]

# Parses equation string into recursive list for eval_eq.
# Example:
#   in: '(/ (+ net_assets net_profit) loans)'
#  out: ['(+ net_assets net_profit)', '(/ (+ net_assets net_profit) loans)']
def eq_helper(eq):
    
    parens = [] # Keeps list of index location of open parentheses.
    parts  = [] # Collects parts of equation string.
    
    # Iterate through equation string, remembering positions of open parens,
    # and collecting substrings between open and closed parens.
    for c in range(0, len(eq)):
    	# Remember position of open positions.
        if eq[c] == '(' : parens.append(c)
        # Create substring from open to closing paren.
        if eq[c] == ')' : parts.append(eq[parens.pop() : c+1])

    return parts

# Takes output from eq_helper to calculate operations on columns.
# param eq_list The list returned from eq_helper.
def eval_eq(eq_list):

	# banki_complete.csv has all the indicators, so we can use it
	# to calculate new values for our current dataframe.
	banki = pd.read_csv('../csv/banki_complete.csv', index_col=False)
    
    # Create temporary columns for extended operations.
	tmp_col = 0

	# By the final calculation, eq_list will become the value
	# of the Series we want.
	while type(eq_list) != pd.Series:
    
		this = eq_list[0]          # Set working equation part to first element.
		operator = this[1]            # Set operator.
		operands = this[3:-1].split() # Set operands.
        
        # Check names for validity.
		bad_names = []
		for op in operands:
			if not op in list(banki.columns):
				bad_names.append(op)
		if len(bad_names) > 0:
			print 'There were invalid indicator names found in equation',this
			print 'Invalid:', bad_names
			print 'Run `python parser.py -i` for full list of indicators.'
			raise SystemExit(0)
        
        # The result begins with the value of the first operand.
		tmp_result = banki[operands[0]]

        # For each operand.
		for op in range(1, len(operands)):
			# Set the column with which to operate.
			op_value = banki[operands[op]]
    
            # Math.
			if operator == '/': tmp_result = tmp_result / op_value
			if operator == '*': tmp_result = tmp_result * op_value
			if operator == '+': tmp_result = tmp_result + op_value
			if operator == '-': tmp_result = tmp_result - op_value
			if operator == '^': tmp_result = tmp_result ** op_value
        
        # If len > 1, there are more parts to calculate.
		if len(eq_list) > 1:
			# Bump up the temporary column.
			tmp_col += 1
			# Set the temporary column to our temporary result.
			banki[str(tmp_col)] = tmp_result
			# Replace the part of the equation we just calculted with the
			# name of temporary column. It will be called in next calculations.
			eq_list[-1] = eq_list[-1].replace(this, str(tmp_col))      
			# Remove first element, now that we've finished. 
			eq_list = eq_list[1:]
			# If there are no more elements, then tmp_result is final result.
		else:
			eq_list = tmp_result

	return eq_list


# Puts all the equation helper functions together to add string equations passed
# from the command line to the model_data DataFrame.
# param df The DataFrame to which to add the results of the equations.
# param eq_list The string equations passed from the command line.
def add_eqs(df, eq_list):

    # For each equation passed from the command line...
	for eq in eq_list:
        # Get the recursive form of the equation.
		recursive_eq_str = eq_helper(eq)
		# Evaluate the column.
		col = eval_eq(recursive_eq_str)
		# Create a syntatically appropriate column name.
		eq_str_col_name = eq.replace(' ','_')
		# Add it to the DataFrame
		df.insert(len(df.columns), eq_str_col_name, col)

	#df.replace(np.inf, np.nan)

	return df
####################################

# Parse args.select
if args.select == None: args.select = []
parsed_args = parse_select(args.select)

singular_cols  = parsed_args[0]
range_cols     = parsed_args[1]
equation_cols  = parsed_args[2]

print 'Loading banki.ru...'
banki_complete = load_banki(update = args.update, redownload=args.redownload)

### Add singular columns first. ###
model_data = banki_complete[['lic_num','period','months'] + singular_cols]

### Add ! columns. ###
if len(range_cols) > 0: print 'Calculating ranges...'
for col in range_cols:
    
    r = get_ratio(col) # Ratios defined in dictionaries.py

    model_data[col + '!'] = banki_complete[col].apply(
    	lambda x: r[0] <= x <= r[1] if pd.notnull(x) else None
    	)

### Add equation columns. ###
if len(equation_cols) > 0: print 'Evaluating expressions...'
model_data = add_eqs(model_data, equation_cols)

### Finish ###

print 'Writing to csv...'
model_data.to_csv('../csv/model_data.csv', index=False)