import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import math

import Mesh_node

class Dis(object):
	def __init__(self, node1, node2):
		self.dis = math.sqrt((node1.x_pos-node2.x_pos)**2+(node1.y_pos-node2.y_pos)**2)

	@classmethod
	def cal_dis(self):
		return self.dis