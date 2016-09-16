import subprocess
import numpy as np

# Array of C values to run model on
vals = np.array([ 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 0.75, 0.9, 0.95, 1.0 ])

# Create header of results file
fileName = "../out/c_results.txt"
with open(fileName, "w") as myfile:
	myfile.write("Results of C-value testing\n\n")
	myfile.close()

# Iterate over test values for C, run script
for C in vals:
	subprocess.call(["./multinomial_logistic_regression.py", str(C)])
print("\nResults stored in %s" % fileName)
