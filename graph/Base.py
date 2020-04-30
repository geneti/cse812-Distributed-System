import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import math
import copy

import Gaussian_2d, NodeDistribution, Mesh_node, Mesh_link
import Node_distance, IR
# hyper parameters
Num = 100
gateway_prob = 0.05
path_loss = 1
# links interference range list from 0 to 11
G = [2, 1.125, 0.75, 0.375, 0.125, 0,0,0,0,0,0,0]
F = [0,0,0.0009,0.0175,0.1295,0.3521,0.3521,0.1295,0.0175,0.0009,0,0]
Minkowski = 2
interference_ceiling = 10**8 # when the distance between two links is 0, we set a large constant value here

def main():
	# generate location matrix
	t = NodeDistribution.location_matrix(Num, 'Gaussian_2d')
	LM = t.generate()
	# generate nodes
	Nodes = [Mesh_node.Node(gateway_prob, LM.iloc[i,0], LM.iloc[i,1], i) for i in range(len(LM))]
	# calculate the interference range between nodes and generate links
	# Note: link (a->b) and (b->a) cannot exist at the same time
	Links = [];
	for i in range(len(Nodes)):
		for j in range(len(Nodes)):
			if i == j:
				continue
			dis = Node_distance.Dis.cal_dis(Nodes[i], Nodes[j])
			# node interference range
			nir = IR.Node_IR(Nodes[i], Nodes[j], path_loss)
			node_ir = nir.ir
			if node_ir >= dis:
				Links.append(Mesh_link.Link(Nodes[i], Nodes[j]))
				Nodes[i].out_neighbours.append(j)
				Nodes[j].in_neighbours.append(i)
	print('link list generated')

	# caculate minimum hop count for each node by BFS
	for i in range(len(Nodes)):
		mhc = 1
		if Nodes[i].is_gateway == 1:
			Nodes[i].min_hop_count = mhc
			continue
		queue = []
		vis = []
		queue.append(i)
		vis.append(i)
		while queue:
			s = queue.pop(0)
			mhc += 1
			for j in Nodes[i].out_neighbours:
				if Nodes[j].is_gateway == 1:
					break
				if j in vis:
					continue
				queue.append(j)
				vis.append(j)
		Nodes[i].min_hop_count = mhc
	print('minimum hop count calculated')

	# calculate rank for each link
	for i in range(len(Links)):
		link_neighbours = len(Links[i].node1.out_neighbours) + len(Links[i].node2.in_neighbours)
		link_min_hop_count = min(Links[i].node1.min_hop_count, Links[i].node2.min_hop_count)
		link_distance = Links[i].distance
		Links[i].rank = link_neighbours * link_distance**2 * Links[i].node2.Rx_th / (link_min_hop_count * \
						Links[i].node1.pt * Links[i].node1.gain * Links[i].node2.gain)
	print('rank list generated of length: ', len(Links))

	# create deep copy of links list and sort in descending order by rank
	def take_rank(elem):
		# elem is a link object
		return elem.rank
	des_links_list = copy.deepcopy(Links)
	des_links_list.sort(key = take_rank)

	for it in range(len(des_links_list)):
		if it%200==0:
			print(it)
		Score = np.zeros(12)
		node_s = des_links_list[it].node1
		node_t = des_links_list[it].node2
		# calculate score for each possible channel
		for omega in range(12):
			if it != 0:
				for j in range(it):
					delta_omega = abs(omega - des_links_list[j].channel)
					node_p = des_links_list[j].node1
					node_q = des_links_list[j].node2
					D_pt = Node_distance.Dis.cal_dis(node_p, node_t)
					D_sq = Node_distance.Dis.cal_dis(node_s, node_q)
					D_sp = Node_distance.Dis.cal_dis(node_s, node_p)
					D_tq = Node_distance.Dis.cal_dis(node_t, node_q)

					Min_dis = min(min(D_pt, D_sp), min(D_sq, D_tq))
					if Min_dis == D_pt:
						nir = IR.Node_IR(node_p, node_t, path_loss)
						NIR = nir.ir
					elif Min_dis == D_sp:
						# when calculate the IR for 2 transmitters, choose the bigger one
						nir1 = IR.Node_IR(node_p,node_s,path_loss)
						nir2 = IR.Node_IR(node_s, node_p, path_loss)
						NIR = max(nir1.ir, nir2.ir)
					elif Min_dis == D_sq:
						nir = IR.Node_IR(node_s, node_q, path_loss)
						NIR = nir.ir
					elif Min_dis == D_tq:
						# when calculate the IR for 2 transmitters, choose the bigger one
						nir1 = IR.Node_IR(node_t,node_q,path_loss)
						nir2 = IR.Node_IR(node_q, node_t, path_loss)
						NIR = max(nir1.ir, nir2.ir)

					# score the current possible channel
					# assume the busy idle ratio for 2 links is the average
					bil = (des_links_list[j].busy_idle_ratio + des_links_list[it].busy_idle_ratio)/2
					if delta_omega < 5:
						Score[omega] += 0
					elif Min_dis <= NIR:
						Score[omega] += NIR/Min_dis * bil
					else:
						Score[omega] += interference_ceiling
								
		# call set_channel function
		des_links_list[it].set_channel_base(Score)



if __name__ == '__main__':
	main()