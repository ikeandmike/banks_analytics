################################### PREAMBLE ###################################

import os
import datetime

from ModelResults import ModelResults # Class I made for storing details (used for exporting to txt file, for creating graphs etc.)

 ############################### HELPER FUNCTIONS ###############################

def draw_line():
	return "--------------------------------------------------------------------------------\n\n"

def make_header(f, date, time):
	f.write("WPI/Deloitte Regression Model for Predicting License Revocation of Russian Banks\n")
	f.write("Test Performed: %s %s\n\n" % (date, time))
	f.write(draw_line())

################################ FILE WRITERS ##################################

# Generates an extended report (data + results)
def long_rep(f, r, date, time):
	make_header(f, date, time)

	f.write("Training Data:\n")
	f.write("X_train=\n")	
	f.write(r.X_train)
	f.write("\nY_train=\n")
	f.write(r.Y_train)
	f.write("\n\n")
	
	f.write("Testing Data:\n")
	f.write("X_test=\n")
	f.write(r.X_test)
	f.write("\nY_test=\n")
	f.write(r.Y_test)
	f.write("\n\n")
	f.write(draw_line())
	
	f.write("Results:\n\n")
	f.write("Prediction Array (Predictions of Y_test):\n")
	f.write(r.predict_arr)
	f.write("\nProbability Vectors:\n")
	f.write(r.prob_arr)
	f.write("\n\n")
	f.write("Percentage of Total Predictions Correct: %s\n" % r.per_corr)
	f.write("Precision:\n")
	f.write(r.precision)
	f.write("\nRecall:\n")
	f.write(r.recall)
	f.write("\nF1:\n")
	f.write(r.f1)
	f.write("\n")
	f.write(draw_line())

	f.close()

# Generates a summary (just results)
def short_rep(f, r, date, time):
	make_header(f, date, time)	
	
	f.write("Results:\n\n")
	f.write("Percentage of Total Predictions Correct: %s\n" % r.per_corr)
	f.write("Precision:\n")
	f.write(r.precision)
	f.write("\nRecall:\n")
	f.write(r.recall)
	f.write("\nF1:\n")
	f.write(r.f1)
	f.write("\n")
	f.write(draw_line())

	f.close()

# Writes run reports to txt files, returns paths to files
def export_test(r):
	# Get the current date/time
	date = str(datetime.date.today())
	time = str(datetime.datetime.now().time())[:8]

	# Create folder "../out/<date>/", if it doesn't exist already
	path = "../out/%s/" % date
	if not os.path.exists(path):
    		os.makedirs(path)

	# Create file pointers
	write_file1 = "%s%s_extended.txt" % (path, time)
	f = open(write_file1, 'w')
	write_file2 = "%s%s_brief.txt" % (path, time)
	g = open(write_file2, 'w')

	# Generate reports
	long_rep(f, r, date, time)
	short_rep(g, r, date, time)

	return write_file1, write_file2
