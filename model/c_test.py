################################### PREAMBLE ###################################

import subprocess
import numpy as np

from export_test import *

# USAGE: This script runs multinomial_logistic_regression.py on the same seed
#        with different C values to compare them. The vals array below contains
#        the C values that the script will iterate over. Change it to include
#        whichever values you want.

#################################### SCRIPT ####################################

# Array of C values to run model on
vals = np.array([ 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 0.75, 0.9, 0.95, 1.0 ])

fileName = path + "c_test.txt" # Create header of results file

generate_path() # Create folders if they don't exist

with open(fileName, "w") as myfile:
	myfile.write("Results of C-value testing\n")
	myfile.close()

# Iterate over test values for C, run model on same seed to get comparative results
for C in vals:
	subprocess.call(["./multinomial_logistic_regression.py", "-ct", fileName, "-c", str(C), "-s", "42"])
print("\nResults stored in %s" % fileName)
