import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import math

import Gaussian_2d, NodeDistribution

class Node(object):
	def __init__(self, gateway_prob, x, y, index):
		# node index 1:Num
		self.index = index
		# Location info
		self.x_pos = x
		self.y_pos = y
		# transmit power
		self.pt = 1
		# antenna gain, dB unit
		self.gain = 1
		# node height
		self.height = 1
		# Carrier sense threshold
		self.CS_th = 1
		# Reciever threshold
		self.Rx_th = 1
		# judge the node is or not a gateway
		self.is_gateway = np.random.binomial(1, gateway_prob)
		# numbers of neighbour within interference range; elements are index not instance
		self.neighbours = []
		# min hop count
		self.min_hop_count = 1000
		# transmit node interference range
		self.Tranmit_IR = 

