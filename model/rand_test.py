import numpy as np
import argparse
from random import randrange
from export_test import * # For outputting results to txt
from sklearn.metrics import precision_score, recall_score, f1_score

# Argument Parsing
parser = argparse.ArgumentParser()
runType = parser.add_mutually_exclusive_group()
runType.add_argument("-t", "--runType", help="Pass 'month' or 'quarter'")
yArr = parser.add_mutually_exclusive_group()
yArr.add_argument("-y", "--y_test", help="Pass filename file containing Y_test from model run")
args = parser.parse_args()

if args.y_test == None:
	print("ERROR: Provide Y_test file with the '-y' option.")
	exit()

# Load Y_test (expected values)
Y_test = np.loadtxt(args.y_test)

# Create random array
rand_arr = np.array([])

# Generate a random array the same size as Y_test
for i in range(0, Y_test.size):
	# Generate new random value (in range depending on type)
	if args.runType == "month":
		val = randrange(1, 27)
		if val == 25: val = 1000
		elif val == 26: val = 9000
	elif args.runType == "quarter":
		val = randrange(1, 11)
		if val == 9: val = 1000
		elif val == 10: val = 9000
	else:
		print("ERROR: Input '-t' and either 'month' or 'quarter'")
		exit()

	# Add random value to array
	rand_arr = np.append(rand_arr, val)

precision = precision_score(Y_test, rand_arr, average=None)	# Calculate the precision
recall    = recall_score(Y_test, rand_arr, average=None)	# Calculate the recall
f1        = f1_score(Y_test, rand_arr, average=None)		# Calculate f1

print("Precision: %s\n" % precision)
print("Recall: %s\n" % recall)
print("f1: %s\n" % f1)

generate_path() # Generate results filepath
output_arr(precision, "precision.csv")
output_arr(recall, "recall.csv")
output_arr(f1, "f1.csv")
