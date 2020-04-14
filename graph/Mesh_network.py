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
# links interference range list from 0 to 11
MIR = [2, 1.125, 0.75, 0.375, 0.125, 0,0,0,0,0,0,0]

def main():
	# generate location matrix
	t = NodeDistribution.location_matrix(Num, 'Gaussian_2d')
	LM = t.generate()
	# generate nodes
	Nodes = [Mesh_node.Node(gateway_prob, LM.iloc(i,0), LM.iloc(i,1), i) for i in range(len(LM))]
	# calculate the interference range between nodes and generate links
	# Note: link (a->b) and (b->a) cannot exist at the same time
	Links = [];
	for i in range(len(Nodes)-1):
		for j in range(i+1, len(Nodes)):
			dis = math.sqrt((Nodes[i].x_pos - Nodes[j].x_pos)**2+(Nodes[i].y_pos - Nodes[j].y_pos)**2)
			# node interference range
			node_ir = math.sqrt(Nodes[i].pt * Nodes[i].gain * Nodes[j].gain * Nodes[i].height**2\
								 * Nodes[j].height**2 / Nodes[j].CS_th) * path_loss
			if node_ir >= dis:
				Links.append(Mesh_link.Link(Nodes[i], Nodes[j]))
				Nodes[i].neighbours.append(j)
				Nodes[j].neighbours.append(i)

	# caculate minimum hop count for each node by BFS
	for i in range(len(Nodes)):
		mhc = 0
		if Nodes[i].is_gateway() == 1:
			Nodes[i].min_hop_count = 0
			continue
		queue = []
		vis = []
		queue.append(i)
		vis.append(i)
		while queue:
			s = queue.pop(0)
			mhc += 1
			for j in Nodes[i].neighbours:
				if Nodes[j].is_gateway() == 1:
					break
				if j in vis:
					continue
				queue.append(j)
				vis.append(j)
		Nodes[i].min_hop_count = mhc

	# calculate rank for each link
	for i in range(len(Links)):
		link_neighbours = len(Links[i].node1.neighbours) + len(Links[i].node2.neighbours)
		link_min_hop_count = min(Links[i].node1.min_hop_count, Links[i].node2.min_hop_count)
		link_distance = Links[i].distance
		Links[i].rank = link_neighbours * link_distance**2 * Links[i].node2.Rx_th / (link_min_hop_count * \
						Links[i].node1.pt * Links[i].node1.gain * Links[i].node2.gain)

	# create deep copy of links list and sort in descending order by rank
	def take_rank(elem):
		# elem is a link object
		return elem.rank
	des_links_list = copy.deepcopy(Links)
	des_links_list.sort(key = take_rank)



if __name__ = '__main__':
	main()