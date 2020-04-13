import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import math

import Gaussian_2d, NodeDistribution

class Link(object):
	def __init__(self, node1, node2):
		self.node1 = node1
		self.node2 = node2
		# channel should be assigned between [1,12]
		self.channel = -1
		self.busy_idle_ratio = 0.9
		