#!/usr/bin/python

################################### PREAMBLE ###################################

import csv, sys, argparse, subprocess
import numpy as np
from timeit import default_timer
from sklearn.preprocessing import scale
from sklearn import linear_model, ensemble
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score

# Class I made for storing details (used for exporting results to txt file)
from ModelResults import ModelResults
# A file I wrote to export results
from export_test import *

np.set_printoptions(threshold=np.inf) 	# Turns off truncation (forces numpy to print large arrays)
np.set_printoptions(precision=3) 	# Sets number of printed digits

# These two arrays contain the top and bottom 20 banks in terms of net assets as ranked on Banki.ru on 27/09/16
top_banks = [1481,1000,354,2209,1623,3349,1326,3466,1978,3251,1,2562,3292,2272,2748,328,2888,436,963,2289]
bottom_banks = [3430,3420,3309,3353,2688,3318,3514,384,2605,2435,3343,3502,3509,3427,3511,3447,3483,3324,149,3332]

################################## MODEL CODE ##################################

start_time = default_timer() # To measure program execution time

print("WPI/Deloitte Model for Predicting License Revocation of Russian Banks\n")

# Argument Parsing
parser = argparse.ArgumentParser()
desc = parser.add_mutually_exclusive_group()
desc.add_argument("-d", "--description", help="Give text to describe model run type. Will be stored in description.txt")
seed_par = parser.add_mutually_exclusive_group()
seed_par.add_argument("-s", "--seed", help="Pass seed for train_test_split.")
c_par = parser.add_mutually_exclusive_group()
c_par.add_argument("-c", "--pass_c", help="Pass in value for C for model to use. Only used when running LogisticRegression")
c_test = parser.add_mutually_exclusive_group()
c_test.add_argument("-ct", "--c_test", help="Used by c_test.py to output several runs to one file; give this option the path to the file where all results should be stored. Only used when running LogisticRegression")
args = parser.parse_args()

# Write description to txt file if given
if args.description != None:
	generate_path() # Generate folders for path if they don't exist

	descFile = path + "description.txt"
	with open(descFile, "w") as fp:
		fp.write(args.description)
		fp.close()

call_parse = ["../parser/parser.py", "-s"]

normatives                           = ["N1", "N1_0", "N1_1", "N1_2", "N2", "N3", "N4", "N7", "N9_1", "N10_1", "N12"]
loans_to_businesses_and_institutions = ["for_a_term_of_up_to_6_months", "for_a_term_of_6_months_to_1_year", "for_a_term_of_1_year_to_3_years", "for_a_term_over_3_years"]
ratios                               = ["return_on_net_assets", "return_on_equity", "reserve_to_loans", "mortgaged_property_to_loans", "foreign_currency_operations_to_net_assets"]
custom_ratios                        = ['"(/ interbank_credit_in_cbr_turnover interbank_credit_in_cbr)"', '"(/ overdue_debt_1 overdrafts)"', '"(/ attracted_interbank_loans_from_cbr_turnover attracted_interbank_loans_from_cbr)"']
# NOTE: custom_ratios must be enclosed in double quotes for the parser to read them correctly

# Created feature set this way because of the length of the strings
# To add features, append feature strings to *this* array
features = normatives + loans_to_businesses_and_institutions + ratios + custom_ratios
call_parse += features

# Run parser to generate custom model_data.csv file
print("Generating datafile...")
try:
	subprocess.call(call_parse, cwd="../parser") # cwd = Current Working Directory
except WindowsError: # subprocess.call doesn't work on Windows
	print("\nWARNING: Auto-generation of model data not supported in Windows. Please run 'python parser.py' before running model to update model_data.csv file\n\n")	

print("Importing data...")
with open('../csv/model_data.csv', 'rb') as csvfile:
	my_reader = csv.reader(csvfile)	
	firstRow = True		# So that loop runs different code on first row
	i = 0			# Keep track of loop number

	for row in my_reader:	# Iterate over all rows in csv
		if firstRow == False:
			
			target = float(row[2])	# Get target value from file
			lic_num = float(row[0]) # Get license number from file

			# Ignore negative targets (ie. values from after revocation)
			# Uncomment rest of line to exclude extreme banks
			if target > 0: # and lic_num not in top_banks and lic_num not in bottom_banks:
				
				# Generate array of features in this row
				new_feat = []
				for j in range(3, numFeatures+3): # Iterate over features, add to array
					curr_feat = row[j]

					# No data provided for this feature
					if curr_feat == "":
						new_feat.append(float(0))	# Meaningless value
						new_feat.append(float(0))	# 0 = Value missing

					else:
						# Boolean values provided (for reporting in bounds / out of bounds)
						if curr_feat == "True":
							new_feat.append(float(1))	# 1 = In Bounds 

						elif curr_feat == "False":
							new_feat.append(float(0))	# 0 = Out of Bounds

						# Numeric value provided (normal -- value of feature)
						else:
							new_feat.append(float(curr_feat)) # Use value of feature

						new_feat.append(float(1)) # 1 = Value present

				X = np.concatenate(( X, np.array([new_feat]) )) # Add new feature set to array

				# Uncomment to run on all 26 classes, and comment out the QUARTERLY block				
				#Y = np.append(Y, target)
				
				# QUARTERLY
				if target <= 3: Y = np.append(Y, 1)
				elif target <= 6: Y = np.append(Y, 2)
				elif target <= 9: Y = np.append(Y, 3)
				elif target <= 12: Y = np.append(Y, 4)
				elif target <= 15: Y = np.append(Y, 5)
				elif target <= 18: Y = np.append(Y, 6)
				elif target <= 21: Y = np.append(Y, 7)
				elif target <= 24: Y = np.append(Y, 8)
				else: Y = np.append(Y, target)
				

		else:
			firstRow = False
			numFeatures = len(row)-3 # Everything past first three columns are features

			# Create array of feature labels
			feature_labels = []
			for j in range(3, numFeatures+3):
				feature_labels.append(row[j])		# Add feature name
				feature_labels.append("%s_M?" % row[j])	# For "missing" column (1 if feature present, 0 if not)

			# Create the feature and target datasets respectively
			X = np.empty((0,numFeatures*2), float) # Create empty array with shape attributes (so it can be used in concatenate)
			Y = np.array([])

		# Print dots to indicate progress
		if i % 350 == 0:
			sys.stdout.write('.')
			sys.stdout.flush()
		i += 1

feature_labels = np.array(feature_labels) # Convert feature_labels to a numpy ndarray

# Split data into testing & training, with 66% training, 33% testing
# If seed passed, use it
# Otherwise, seed used to keep split consistent
if args.seed != None:
	X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33, random_state=int(args.seed), stratify=Y)
else:
	X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33, random_state=42, stratify=Y)

# Data preprocessing (uncomment below to add preprocessing)
# scale(X_train, copy=False)
# scale(X_test, copy=False)

print("\nFitting model...")
# Store results in ModelResults object
results = ModelResults(X_train, X_test, Y_train, Y_test, feature_labels)

# If passed, use passed in C value
# c_val is only relevant to LogisticRegression, but for compatibility with
# ModelResults objects, a value is included either way
if args.pass_c != None: c_val = float(args.pass_c)
else:		      	c_val = 0.01

# Create the model & fit to training data
# Uncomment line to run LogisticRegression
model = linear_model.LogisticRegression(penalty='l1', multi_class='ovr').fit(X_train, Y_train)
#model = ensemble.RandomForestClassifier().fit(X_train, Y_train)

print("Generating predictions...")
predict_arr = model.predict(X_test)	  # Run a prediction for test dataset (ie. compare this array to Y_test)
prob_arr    = model.predict_proba(X_test) # Runs prediction, outputs probability vectors

print("Evaluating performance...")
precision = precision_score(Y_test, predict_arr, average=None)	# Calculate the precision
recall    = recall_score(Y_test, predict_arr, average=None)	# Calculate the recall
f1        = f1_score(Y_test, predict_arr, average=None)		# Calculate f1

exec_time = default_timer() - start_time # Calculate execution time

# Add results to "results" object
# Uncomment this line when running LogisticRegression
results.addResults(c_val, model.coef_, predict_arr, prob_arr, precision, recall, f1, exec_time)
#results.addResults(c_val, model.feature_importances_, predict_arr, prob_arr, precision, recall, f1, exec_time)

# If running with c_test option, export results
# Uncomment for LogisticRegression
#if args.c_test != None:
#	export_c_test(results, args.c_test)
#	exit() # Quit early so full results aren't exported

print("\nTotal Execution Time: %f seconds\n" % exec_time)

# Uncomment for LogisticRegression
#print("\nC: %s\n" % c_val)
print("Precision: %s\n" % precision)
print("Recall: %s\n" % recall)
print("f1: %s\n" % f1)

print("Exporting results...")
export_test(results)
print("Data sets and results exported to %s" % path)

################################################################################
