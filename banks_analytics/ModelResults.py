import numpy as np
from math import log10, floor

class ModelResults:

############################### CLASS FUNCTIONS ################################

	def __init__(self, X_train, X_test, Y_train, Y_test):
		# Round values in X array before storing		
		self.round_2d_arr(X_train, 3)
		self.round_2d_arr(X_test, 3)
		
		self.X_train = str(X_train)
		self.X_test  = str(X_test)
		self.Y_train = str(Y_train)
		self.Y_test  = str(Y_test)

		self.coef = np.array([])

		self.predict_arr = np.array([])
		self.prob_arr    = np.array([])
		self.per_corr    = 0.0
		self.precision    = ""
		self.recall      = ""
		self.f1          = ""

	def addResults(self, coef, predict_arr, prob_arr, per_corr, precision, recall, f1):
		# Round values in prob_arr before storing		
		self.round_2d_arr(prob_arr, 3)

		self.coef	 = str(coef)
		self.predict_arr = str(predict_arr)
		self.prob_arr    = str(prob_arr)
		self.per_corr    = self.n_sig_figs(per_corr, 3)
		self.precsion    = str(precision)
		self.recall      = str(recall)
		self.f1          = str(f1)

############################### HELPER FUNCTIONS ###############################

	# Rounds x to n significant figures
	def n_sig_figs(self, x, n):
		# x = 10 ^ (log10(x)), the floor of which is the number of places the first significant digit is away from the decimal point (in one direction)
		# And the round() function rounds n places after the decimal place (or before, if n is negative)
		# So without adding in -(n-1), it rounds to one significant figure    
		if x == 0: return 0
		return round(x, -(int(floor(log10(abs(x))))-(n-1)))

	# Rounds all the elements in an 2d numpy array to n significant figures
	def round_2d_arr(self, arr, n):
		bounds = arr.shape

		for i in range(bounds[0]):		# Iterate over vectors in array
			for j in range(bounds[1]): 	# Iterate over elements in vector
				arr[i][j] = self.n_sig_figs(arr[i][j], n)

################################################################################
