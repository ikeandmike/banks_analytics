################################### PREAMBLE ###################################

import os
import datetime
import numpy as np

from ModelResults import ModelResults # Class I made for storing details (used for exporting to txt file, for creating graphs etc.)

date = str(datetime.date.today())
time = str(datetime.datetime.now().time())[:8]

############################# CREATE PATH VARIABLE #############################

path = "../out/%s/%s/" % (date, time)
if not os.path.exists(path): # Create folders if they don't exist
	os.makedirs(path)

############################### HELPER FUNCTIONS ###############################

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
	with file(var_path, 'w') as outfile:
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

	c_path = path + "c.txt"
	with file(c_path, 'w') as outfile:
		outfile.write(str(r.C))
		outfile.close()

# Creates files for all results
def export_results(r):
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
	export_data_sets(r)
	export_results(r)

################################################################################
