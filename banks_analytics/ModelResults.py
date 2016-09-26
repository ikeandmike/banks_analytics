import numpy as np
from math import log10, floor

class ModelResults:

############################### CLASS FUNCTIONS ################################

	def __init__(self, X_train, X_test, Y_train, Y_test, feature_labels):
		# Round values in X array before storing		
		self.round_2d_arr(X_train, 3)
		self.round_2d_arr(X_test, 3)
		
		self.X_train = X_train
		self.X_test  = X_test
		self.Y_train = Y_train
		self.Y_test  = Y_test
		self.feature_labels = feature_labels

		self.coef = np.array([])
		self.predict_arr = np.array([])
		self.prob_arr    = np.array([])
		self.precision   = np.array([])
		self.recall      = np.array([])
		self.f1          = np.array([])

	def addResults(self, C, coef, predict_arr, prob_arr, precision, recall, f1):

		self.C		 = C
		self.coef	 = coef
		self.predict_arr = np.array(predict_arr)
		self.prob_arr    = np.array(prob_arr)
		self.precision = np.array(precision)
		self.recall    = np.array(recall)
		self.f1        = np.array(f1)

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
