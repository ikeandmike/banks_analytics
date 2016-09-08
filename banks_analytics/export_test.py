import os
import datetime

def draw_line():
	return "--------------------------------------------------------------------------------\n\n"

# Writes run report to a txt file, returns path to file
def export_test(X_train, Y_train, X_test, Y_test, accuracy, predict_arr, prob_arr):
	# Get the current date/time
	date = str(datetime.date.today())
	time = str(datetime.datetime.now().time())[:8]

	# Create folder "date/" within current directory, if it doesn't exist already
	path = "%s/" % date
	if not os.path.exists(path):
    		os.makedirs(path)

	write_file = "%s%s.txt" % (path, time)
	f = open(write_file, 'w')

	f.write("WPI/Deloitte Regression Model for Predicting License Revocation of Russian Banks\n")
	f.write("Test Performed: %s %s\n\n" % (date, time))
	f.write(draw_line())

	f.write("Training Data:\n")
	f.write("X_train=")	
	f.write(X_train)
	f.write("\nY_train=")
	f.write(Y_train)
	f.write("\n\n")
	
	f.write("Testing Data:\n")
	f.write("X_test=")
	f.write(X_test)
	f.write("\nY_test=")
	f.write(Y_test)
	f.write("\n\n")
	f.write(draw_line())
	
	f.write("Results:\n\n")
	f.write("Accuracy (Percentage of Predictions Correct): %s\n" % accuracy)
	f.write("Prediction Array (Predictions of Y_test):")
	f.write(predict_arr)
	f.write("\nProbability Vectors:")
	f.write(prob_arr)
	f.write("\n\n")
	f.write(draw_line())

	f.close()
	return write_file
