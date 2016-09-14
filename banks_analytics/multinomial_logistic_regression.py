################################### PREAMBLE ###################################

import csv
import sys
import datetime
from math import log10, floor
import numpy as np
from sklearn import linear_model
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.cross_validation import train_test_split

from export_test import export_test # A file I wrote to export results to a txt file

# WARNING: Normally, large numpy arrays are truncated (ie. [ 1, 2, ... , 9999, 10000 ] )
#          This option turns this feature off, so that the entire array can be printed
#          BE CAREFUL WHAT YOU PRINT
np.set_printoptions(threshold=np.inf)
np.set_printoptions(precision=3) # This one is a lot less scary, just sets number of printed digits

############################### HELPER FUNCTIONS ###############################

# Rounds x to n significant figures
def n_sig_figs(x, n):
	# x = 10 ^ (log10(x)), the floor of which is the number of places the first significant digit is away from the decimal point (in one direction)
	# And the round() function rounds n places after the decimal place (or before, if n is negative)
	# So without adding in -(n-1), it rounds to one significant figure    
	if x == 0: return 0
	return round(x, -(int(floor(log10(abs(x))))-(n-1)))

# Rounds all the elements in an 2d numpy array to n significant figures
def round_2d_arr(arr, n):
	bounds = arr.shape

	for i in range(bounds[0]):		# Iterate over vectors in array
		for j in range(bounds[1]): 	# Iterate over elements in vector
			arr[i][j] = n_sig_figs(arr[i][j], n)

# Prepare data for printing (round and convert to str)
def convert_data(X_train, Y_train, X_test, Y_test, per_corr, predict_arr, prob_arr):
	# Round training/test data, accuracy, and probability vectors
	round_2d_arr(X_train, 3)
	round_2d_arr(X_test, 3)
	per_corr = n_sig_figs(per_corr, 3)
	round_2d_arr(prob_arr, 3)

	return str(X_train), str(Y_train), str(X_test), str(Y_test), per_corr, str(predict_arr), str(prob_arr)

################################## MODEL CODE ##################################

print("WPI/Deloitte Regression Model for Predicting License Revocation of Russian Banks")
print("Latest Version Written %s\n" % str(datetime.date.today()))

print("Importing data...")
with open('../csv/model_data.csv', 'rb') as csvfile:
	my_reader = csv.reader(csvfile)
	X = np.array([[1,2,3]]) # Going to form our feature dataset (weird Numpy issue requires me to fill instantiate it with dummy data; will drop later)
	Y = np.array([]) 	# Going to form our target dataset	
	firstRow = True		# So that loop skips over first row (which contains header info)
	i = 0			# Keep track of loop number

	for row in my_reader:	# Iterate over all rows in csv file
		if firstRow == False and row[3] != "NA" and row[4] != "NA" and row[5] != "NA": # Check that row is valid
			N1, N2, N3 = float(row[3]), float(row[4]), float(row[5])# Convert input to float
			X = np.concatenate((X, np.array( [[ N1, N2, N3 ]] ))) 	# Add the new entry onto the array
			if row[6] == "Norm" or row[6]  == "NA":			# If bank still has license
				Y = np.append(Y, float(9000))			# Month value = 9000
			elif int(row[12]) > 24:					# If bank will lose license in more than 2 years
				Y = np.append(Y, float(1000))			# Month value = 1000		
			else:
				Y = np.append(Y, float(row[12]))		# Otherwise, grab number of months left from sheet
		else:
			firstRow = False
		
		# Print dots to indicate progress		
		if i % 350 == 0:
			sys.stdout.write('.')
			sys.stdout.flush()
		i += 1

X = np.delete(X, 0, 0) # Remove the initial dummy row

print("\nFitting model...")

X_train, X_test, Y_train, Y_test = train_test_split( X, Y, test_size=0.33, stratify=Y)	# Split data into testing & training, with 66% training, 33% testing
logreg = linear_model.LogisticRegression(penalty='l1', C=0.01)				# Create the model, setting parameters of model
logreg.fit(X_train, Y_train) 								# Train the model on our training set

print("Generating predictions...")
predict_arr = logreg.predict(X_test)	# Run a prediction for test dataset
prob_arr = logreg.predict_proba(X_test)	# Runs prediction, outputs probability vectors

# ERROR on line 91

"""
print("Evaluating performance...")
per_corr  = logreg.score(X_test, Y_test)			# Calculate the percentage correct on test set
precision = precision_score(Y_test, predict_arr, average=None)	# Calculate the precision
recall    = recall_score(Y_test, predict_arr, average=None)	# Calculate the recall
f1        = f1_score(Y_test, predict_arr, average=None)		# Calculate f1
"""

# TODO Graphing stuff will go here..

"""
print("Exporting results...")
cX_train, cY_train, cX_test, cY_test, cPer_corr, cPredict_arr, cProb_arr = convert_data(X_train, Y_train, X_test, Y_test, per_corr, predict_arr, prob_arr)
extended, short = export_test(cX_train, cY_train, cX_test, cY_test, cPer_corr, cPredict_arr, cProb_arr)
print("\nDetailed results written to %s" % extended)
print("Brief    results written to %s" % short)
"""
################################################################################
