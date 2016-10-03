################################### PREAMBLE ###################################

import os
import datetime
import numpy as np

from ModelResults import ModelResults # Class I made for storing details (used for exporting to txt file, for creating graphs etc.)

############################# CREATE PATH VARIABLE #############################

date = str(datetime.date.today())
time = str(datetime.datetime.now().time())[:8]
time = time.replace(":", "-") # Replace colons - Windows paths cannot have them

path = "../out/%s/%s/" % (date, time)

############################### HELPER FUNCTIONS ###############################

# Generates the folders necessary for the path variable (where the output goes)
def generate_path():
	# Create folders if they don't exist
	if not os.path.exists(path):
		os.makedirs(path)

# Saves arr to filename.csv
def output_arr(arr, filename):
	var_path = path + filename		# Create full path to file
	np.savetxt(var_path, arr, delimiter=',')# Save array as csv

# Adds header before exporting to csv
def output_arr_w_header(arr, filename, header):	
	# Create header string	
	head_str = str(header[0])
	for i in range(1, header.size):
		head_str = head_str + "," + str(header[i])
	head_str = head_str + "\n"

	# Output file with header
	var_path = path + filename
	with open(var_path, 'w') as outfile:
		outfile.write(head_str)
		np.savetxt(outfile, arr, delimiter=',')
		outfile.close()

################################ FILE WRITERS ##################################

# Creates four files, one for each data set (X_train, X_test, Y_train, Y_test)
# Also export value of C
def export_data_sets(r):

	output_arr_w_header(r.X_train, "X_train.csv", r.feature_labels)
	output_arr_w_header(r.X_test, "X_test.csv", r.feature_labels)
	output_arr(r.Y_train, "Y_train.csv")
	output_arr(r.Y_test, "Y_test.csv")

	# Uncomment for LogisticRegression
#	c_path = path + "c.txt"
#	with open(c_path, 'w') as outfile:
#		outfile.write(str(r.C))
#		outfile.close()

# Creates files for all results
def export_results(r):
	time_path = path + "execution_time.txt"
	with open(time_path, 'w') as outfile:
		mins = 0
		while r.exec_time > 60:
			mins += 1
			r.exec_time -= 60
		outfile.write(str(mins) + " minutes and " + str(r.exec_time) + " seconds")
		outfile.close()

	output_arr_w_header(r.coef, "coef.csv", r.feature_labels)
	output_arr(r.predict_arr, "predict_array.csv")

	# Create header with target values for some results files	
	header = np.arange(1,25)
	header = np.append(header, [1000, 9000])

	output_arr_w_header(r.prob_arr, "probability_vectors.csv", header)
	output_arr(r.precision, "precision.csv")
	output_arr(r.recall, "recall.csv")
	output_arr(r.f1, "f1.csv")

# Writes run reports to txt files, returns paths to files
# r = a ModelResults object
def export_test(r):
	generate_path()

	export_data_sets(r)
	export_results(r)

# Used by c_test.py to compare several C values on the same model
# Generally don't want to use this manually
def export_c_test(r, filePath):
	with open(filePath, "a") as myfile:
		# Print header with list of features (will print each iteration, not worth trying to fix)
		head_str = "Used features: " + str(r.feature_labels[0])
		for i in range(1, r.feature_labels.size):
			head_str += ", " + str(r.feature_labels[i])
		head_str += "\n\n"
		myfile.write(head_str)

		print("C: %f" % r.C)
		myfile.write("C: %f\n" % r.C)
		myfile.write("Precision:\n%s\n\n" % str(r.precision))
		myfile.write("Recall:\n%s\n\n" % str(r.recall))
		myfile.write("F1:\n%s\n\n" % str(r.f1))
		myfile.close()

################################################################################
