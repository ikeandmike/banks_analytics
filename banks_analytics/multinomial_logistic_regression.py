#!/usr/bin/python

# TO RUN
# python multinomial_logistic_regression.py [ C ]
# Optional C parameter is for testing effectiveness of change in C
# Program runs until performance metrics are calculated, then the values are outputted and the program quits

################################### PREAMBLE ###################################

import csv
import sys
import numpy as np
from sklearn import linear_model
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.cross_validation import train_test_split

from ModelResults import ModelResults	# Class I made for storing details (used for exporting to txt file, for creating graphs etc.)
					# It handles rounding/casting; just pass variables used as is
from export_test import export_test	# A file I wrote to export results to a txt file

# WARNING: Normally, large numpy arrays are truncated (ie. [ 1, 2, ... , 9999, 10000 ] )
#          This option turns this feature off, so that the entire array can be printed
#          BE CAREFUL WHAT YOU PRINT
np.set_printoptions(threshold=np.inf)
np.set_printoptions(precision=3) # This one is a lot less scary, just sets number of printed digits

############################### HELPER FUNCTIONS ###############################

# Validates the list of features
def validateFeatures(row, numFeatures):
	for i in range(3,6):
		if row[i] == "NA": return False

	return True

# TODO Replace above code with this after Jake updates data format
#	for i in range(4, numFeatures+4):
#		if row[i] == "NA": return False
#	return True

# Returns the average of the elements in arr
# Assumes values in arr are numerical
def ave(arr):
	sum = 0
	for item in arr:
		sum += item
	return float(sum) / float(arr.size)

################################## MODEL CODE ##################################

print("WPI/Deloitte Regression Model for Predicting License Revocation of Russian Banks\n")

print("Importing data...")
with open('../csv/model_data.csv', 'rb') as csvfile:
	my_reader = csv.reader(csvfile)	
	firstRow = True		# So that loop skips over first row (which contains header info)
	i = 0			# Keep track of loop number

	for row in my_reader:	# Iterate over all rows in csv
		if firstRow == False:
			if validateFeatures(row, numFeatures):
				
				# Generate array of new features
				new_feat = []
				#for j in range(4, numFeatures+3): # Iterate over features, add to array
				for j in range(3, 6): # TODO Replace this line with the above with new data format
					new_feat.append(float(row[j]))
				X = np.concatenate(( X, np.array([new_feat]) )) # Add the new entry onto the array
			
				#TODO Replace rest of block with this line after data format change
				#Y = np.append(Y, float(row[3])+1) # Get target value from sheet

				if row[6] == "Norm" or row[6]  == "NA":			# If bank still has license
					Y = np.append(Y, float(9000))			# Month value = 9000
				elif int(row[12]) >= 24:				# If bank will lose license in more than 2 years
					Y = np.append(Y, float(1000))			# Month value = 1000
				else:
					Y = np.append(Y, float(row[12])+1)		# Otherwise, grab number of months left from sheet
s
		else:
			firstRow = False
			numFeatures = 3
			#numFeatures = len(row)-4 # Everything past first four columns are features
			# TODO Uncomment this and make changes to if block once Jake changes format of data file
			# Using np.concatenate (see above if block) requires that
			# the two arrays' have the same dimensions
			# This block of code creates a "dummy" first element to
			# make concatenate happy; it will be removed later
			temp_arr = []
			for j in range(numFeatures):
				temp_arr.append(j)
			X = np.array([temp_arr])
			Y = np.array([]) # Going to form our target dataset

		# Print dots to indicate progress		
		if i % 350 == 0:
			sys.stdout.write('.')
			sys.stdout.flush()
		i += 1

X = np.delete(X, 0, 0) # Remove the initial dummy row

print("\nFitting model...")

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33, stratify=Y)	# Split data into testing & training, with 66% training, 33% testing
results = ModelResults(X_train, X_test, Y_train, Y_test)					# Store values in ModelResults object

# Create the model & fit to training data
# If passed, use passed in C value
if len(sys.argv) > 1:	model = linear_model.LogisticRegression(penalty='l1', C=float(sys.argv[1]), multi_class='ovr').fit(X_train, Y_train)
else:			model = linear_model.LogisticRegression(penalty='l1', C=0.01, multi_class='ovr').fit(X_train, Y_train)

print("Generating predictions...")
predict_arr = model.predict(X_test)	    # Run a prediction for test dataset (ie. compare this array to Y_test)
prob_arr    = model.predict_proba(X_test) # Runs prediction, outputs probability vectors

print("Evaluating performance...")
per_corr  = model.score(X_test, Y_test)				# Calculate the percentage correct on test set
precision = precision_score(Y_test, predict_arr, average=None)	# Calculate the precision
recall    = recall_score(Y_test, predict_arr, average=None)	# Calculate the recall
f1        = f1_score(Y_test, predict_arr, average=None)		# Calculate f1

# If C value passed in, add results to file (used in script for testing several values of C)
if len(sys.argv) > 1:
	with open("../out/c_results.txt", "a") as myfile:
		print("C: %f | F1: %f" % (float(sys.argv[1]), ave(f1)))
		myfile.write("C: %f | P: %f | R: %f | F1: %f\n" % (float(sys.argv[1]), ave(precision), ave(recall), ave(f1)))
		myfile.write("Precision:\n%s\n\n" % str(precision))
		myfile.write("Recall:\n%s\n\n" % str(recall))
		myfile.write("F1:\n%s\n\n" % str(f1))
		myfile.close()
	exit() # Quit early so results aren't printed

results.addResults(model.coef_, predict_arr, prob_arr, per_corr, precision, recall, f1) # Add results to "results" objects

print("\nCoefficient Matrix: \n%s\n" % model.coef_)
print("Percent Correct: %s\n" % per_corr)
print("Precision: %s\n" % precision)
print("Recall: %s\n" % recall)
print("f1: %s" % f1)

print("T Precision %s" % ave(precision))
print("T Recall %s" % ave(recall))
print("T F1 %s" % ave(f1))

print("\nExporting results...")
extended, short = export_test(results)
print("Detailed report (data + results) written to %s" % extended)
print("Brief report (results only) written to %s\n" % short)

################################################################################
