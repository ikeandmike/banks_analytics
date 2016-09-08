################################### PREAMBLE ###################################

import os
import datetime

############################### HELPER FUNCTIONS ###############################

def draw_line():
	return "--------------------------------------------------------------------------------\n\n"

def make_header(f, date, time):
	f.write("WPI/Deloitte Regression Model for Predicting License Revocation of Russian Banks\n")
	f.write("Test Performed: %s %s\n\n" % (date, time))
	f.write(draw_line())

################################ FILE WRITERS ##################################

# Generates an extended report
def long_rep(f, X_train, Y_train, X_test, Y_test, accuracy, predict_arr, prob_arr, date, time):
	make_header(f, date, time)

	f.write("Training Data:\n")
	f.write("X_train=\n")	
	f.write(X_train)
	f.write("\nY_train=\n")
	f.write(Y_train)
	f.write("\n\n")
	
	f.write("Testing Data:\n")
	f.write("X_test=\n")
	f.write(X_test)
	f.write("\nY_test=\n")
	f.write(Y_test)
	f.write("\n\n")
	f.write(draw_line())
	
	f.write("Results:\n\n")
	f.write("Accuracy (Percentage of Predictions Correct): %s\n" % accuracy)
	f.write("Prediction Array (Predictions of Y_test):\n")
	f.write(predict_arr)
	f.write("\nProbability Vectors:\n")
	f.write(prob_arr)
	f.write("\n\n")
	f.write(draw_line())

	f.close()

# Generates a summary
def short_rep(f, accuracy, prob_arr, date, time):
	make_header(f, date, time)	
	
	f.write("Results:\n\n")
	f.write("Accuracy (Percentage of Predictions Correct): %s\n" % accuracy)
	f.write("\nProbability Vectors:\n")
	f.write(prob_arr)
	f.write("\n\n")
	f.write(draw_line())

	f.close()

# Writes run reports to txt files, returns paths to files
def export_test(X_train, Y_train, X_test, Y_test, accuracy, predict_arr, prob_arr):
	# Get the current date/time
	date = str(datetime.date.today())
	time = str(datetime.datetime.now().time())[:8]

	# Create folder "date/" within current directory, if it doesn't exist already
	path = "../out/%s/" % date
	if not os.path.exists(path):
    		os.makedirs(path)

	# Create file pointers
	write_file1 = "%s%s_extended.txt" % (path, time)
	f = open(write_file1, 'w')
	write_file2 = "%s%s_brief.txt" % (path, time)
	g = open(write_file2, 'w')

	# Generate reports
	long_rep(f, X_train, Y_train, X_test, Y_test, accuracy, predict_arr, prob_arr, date, time)
	short_rep(g, accuracy, prob_arr, date, time)

	return write_file1, write_file2
