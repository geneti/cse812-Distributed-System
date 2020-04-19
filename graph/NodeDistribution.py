import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import math

import Gaussian_2d

# Get a matrix of (n,2) containing n nodes
class location_matrix(object):
	def __init__(self, Num = 100, method = 'Gaussian_2d'):
		self.Num = Num
		self.distribution = pd.DataFrame()
		self.method = method

	def generate(self):
		if self.method == 'Gaussian_2d':
			t = Gaussian_2d.Gaussian_Distribution(self.Num, [0,0], [[1,0],[0,1]])
			lm = t.get_pdf()
			return lm