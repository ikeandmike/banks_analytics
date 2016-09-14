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
	X = np.array([[1,2,3]]) # Going to form our feature dataset (weird Numpy issue requires me to fill instantiate it with dummy data; will drop later)
	Y = np.array([]) 	# Going to form our target dataset	
	firstRow = True		# So that loop skips over first row (which contains header info)
	i = 0			# Keep track of loop number

	for row in my_reader:	# Iterate over all rows in csv file
#if firstRow == False and row[3] != "NA" and row[4] != "NA" and row[5] != "NA" and row[6] == "Revoked" and int(row[12]) < 24: # Check that row is valid
		if firstRow == False and row[3] != "NA" and row[4] != "NA" and row[5] != "NA":
			N1, N2, N3 = round(float(row[3]), 2), round(float(row[4]), 2), round(float(row[5]), 2)# Convert input to float
			X = np.concatenate((X, np.array( [[ N1, N2, N3 ]] ))) 	# Add the new entry onto the array
			if row[6] == "Norm" or row[6]  == "NA":			# If bank still has license
				Y = np.append(Y, float(9000))			# Month value = 9000
			elif int(row[12]) >= 24:				# If bank will lose license in more than 2 years
				Y = np.append(Y, float(1000))			# Month value = 1000	
			else:
				Y = np.append(Y, float(row[12])+1)		# Otherwise, grab number of months left from sheet
				
		else:
			firstRow = False
		
		# Print dots to indicate progress		
		if i % 350 == 0:
			sys.stdout.write('.')
			sys.stdout.flush()
		i += 1

X = np.delete(X, 0, 0) # Remove the initial dummy row

print("\nFitting model...")

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.5, stratify=Y)	# Split data into testing & training, with 66% training, 33% testing
results = ModelResults(X_train, X_test, Y_train, Y_test)				# Store values in results object
logreg = linear_model.LogisticRegression(penalty='l1', C=0.01).fit(X_train, Y_train)	# Create the model, setting parameters

print("Generating predictions...")
predict_arr = logreg.predict(X_test)	# Run a prediction for test dataset
prob_arr = logreg.predict_proba(X_test)	# Runs prediction, outputs probability vectors

print("Evaluating performance...")
per_corr  = logreg.score(X_test, Y_test)			# Calculate the percentage correct on test set
precision = precision_score(Y_test, predict_arr, average=None)	# Calculate the precision
recall    = recall_score(Y_test, predict_arr, average=None)	# Calculate the recall
f1        = f1_score(Y_test, predict_arr, average=None)		# Calculate f1

results.addResults(predict_arr, prob_arr, per_corr, precision, recall, f1) # Add results to "results" objects

#TODO Run script over several C values, find highest F1 value and corresponding C

print("\nPercent Correct: %s\n" % per_corr)
print("Precision: %s\n" % precision)
print("Recall: %s\n" % recall)
print("f1: %s" % f1)

print("T Precision %s" % ave(precision))
print("T Recall %s" % ave(recall))
print("T F1 %s" % ave(f1))

print("\nExporting results...")
extended, short = export_test(results)
print("Detailed report (data + results) written to %s" % extended)
print("Brief report (results only) written to %s" % short)

################################################################################
