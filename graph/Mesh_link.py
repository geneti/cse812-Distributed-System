import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import math

import Gaussian_2d, NodeDistribution

class Link(object):
	def __init__(self, node1, node2):
		# Note that node1 is the transmitter and node2 is the receiver
		self.node1 = node1
		self.node2 = node2
		# channel should be assigned between [1,12]
		self.channel = 0
		self.busy_idle_ratio = 0.9
		# link rank priority value, not order
		self.rank = 0
		self.distance = math.sqrt((self.node1.x_pos-self.node2.x_pos)**2 + (self.node1.y_pos-self.node2.y_pos)**2)
		# score function for different frequencies of a link
		self.score = np.zeros(12)