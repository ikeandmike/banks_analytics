# fitting the multiomial logistic regression model

import csv
import sys
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn import linear_model

from export_test import export_test # A file I wrote to export results to a txt file

# Notes:
# Currently not restricting output vectors to 24 months (ie. if it guesses that it will be past that, it will show it)

# TODO Fix file export (numpy structs aren't in printable form)

############################### HELPER FUNCTIONS ###############################

# Converts input from CSV from str to float (just to make the code below neater)
def convertNorm(N1, N2, N3):
	return float(N1), float(N2), float(N3)

# Code for running stats on model accuracy, but doesn't work as expected
"""

# Return array of differences between predicted and actual values
def difference(predict, actual):
	assert(predict.size == actual.size)
	ret = np.array([])
	for i in range(predict.size):
		# Going to ignore these for now since it skews the average so
		# much that it has no meaning
		if predict[i] != 9000 and actual[i] != 9000:
			ret = np.append(ret, (predict[i] - actual[i]))
	return ret

# Return the average 
def average(arr):
	sum = 0;
	for i in range(arr.size):
		sum += abs(arr[i])
	return sum/arr.size
"""

################################## MODEL CODE ##################################

print("WPI/Deloitte Regression Model for Predicting License Revocation of Russian Banks")
print("Latest Version Written Sept. 9, 2016\n")

# Import data from csv
with open('banki_cbr_final.csv', 'rb') as csvfile:
	print("Importing data...")
	my_reader = csv.reader(csvfile)
	X = np.array([[1,2,3]]) # Going to form our feature dataset (weird Numpy issue requires me to fill instantiate it with dummy data; will drop later)
	Y = np.array([]) 	# Going to form our target dataset	
	firstRow = True		# So that loop skips over first row (which contains header info)
	i = 0			# Keep track of loop number

	for row in my_reader:	# Iterate over all rows in csv file
		if firstRow == False and row[3] != "NA" and row[4] != "NA" and row[5] != "NA": # Check that row is valid
			N1, N2, N3 = convertNorm(row[3], row[4], row[5])	# Convert input to float
			X = np.concatenate((X, np.array( [[ N1, N2, N3 ]] ))) 	# Add the new entry onto the array
			if row[6] == "Norm" or row[6]  == "NA":			# If bank still has license
				Y = np.append(Y, float(9000))			# Month value = 9000
			else:
				Y = np.append(Y, float(row[12]))		# Otherwise, grab number of months left from sheet
		else:
			firstRow = False
		
		# Print dots to indicate progress		
		if i % 350 == 0:
			sys.stdout.write('.')
			sys.stdout.flush()
		i += 1

print("\nDone parsing data\n")
X = np.delete(X, 0, 0) # Remove the initial dummy row

print("Generating model...")
X_train, X_test, Y_train, Y_test = train_test_split( X, Y, test_size=0.33 )		# Split data into testing & training, with 66% training, 33% testing
logreg = linear_model.LogisticRegression(solver='lbfgs', multi_class='multinomial')	# Create the model, setting parameters of model
logreg.fit(X_train, Y_train) 								# Train the model on our training set
predict_arr = logreg.predict(X_test)							# Run a prediction for test dataset
prob_arr = logreg.predict_proba(X_test)							# Runs prediction, outputs probability vectors
accuracy = str(logreg.score(X_test, Y_test))						# Calculate accuracy (% correct) on test set

print("\nProbability Vectors:\n")
print(prob_arr)

# Exporting results to txt file
report = export_test(X_train, Y_train, X_test, Y_test, accuracy, predict_arr, prob_arr)
print("\nFull results written to %s" % report)

################################################################################
