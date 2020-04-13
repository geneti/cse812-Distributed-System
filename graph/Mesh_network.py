import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import math

import Gaussian_2d, NodeDistribution, Mesh_node, Mesh_link

# hyper parameters
Num = 100
gateway_prob = 0.05
path_loss = 1

def main():
	# generate location matrix
	t = NodeDistribution.location_matrix(Num, 'Gaussian_2d')
	LM = t.generate()
	# generate nodes
	Nodes = [Mesh_node.Node(gateway_prob, LM.iloc(i,0), LM.iloc(i,1), i) for i in range(len(LM))]
	# calculate the interference range between nodes and generate links
	Links = [];
	node_dict = dict.fromkeys(range(Num), []) # a dictionary storing index of links
	for i in range(len(Nodes)-1):
		for j in range(i+1, len(Nodes)):
			dis = math.sqrt((Nodes[i].x_pos - Nodes[j].x_pos)**2+(Nodes[i].y_pos - Nodes[j].y_pos)**2)
			# node interference range
			node_ir = math.sqrt(Nodes[i].pt * Nodes[i].gain * Nodes[j].gain * Nodes[i].height**2\
								 * Nodes[j].height**2 / Nodes[j].CS_th) * path_loss
			if node_ir >= dis:
				Links.append(Mesh_link.Link(Nodes[i], Nodes[j]))
				node_dict[Nodes[i].index].append(Nodes[j].index)
	# caculate minimum hop count for each node by BFS
	for i in range(len(Nodes)):
		mhc = -1


if __name__ = '__main__':
	main()