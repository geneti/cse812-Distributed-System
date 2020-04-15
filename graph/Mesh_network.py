import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import math

import Gaussian_2d, NodeDistribution, Mesh_node, Mesh_link， Node_distance

# hyper parameters
Num = 100
gateway_prob = 0.05
path_loss = 1
# links interference range list from 0 to 11
G = [2, 1.125, 0.75, 0.375, 0.125, 0,0,0,0,0,0,0]
F = [0,0,0.0009,0.0175,0.1295,0.3521,0.3521,0.1295,0.0175,0.0009,0,0]
Minkowski = 2

def main():
	# generate location matrix
	t = NodeDistribution.location_matrix(Num, 'Gaussian_2d')
	LM = t.generate()
	# generate nodes
	Nodes = [Mesh_node.Node(gateway_prob, LM.iloc(i,0), LM.iloc(i,1), i) for i in range(len(LM))]
	# calculate the interference range between nodes and generate links
	# Note: link (a->b) and (b->a) cannot exist at the same time
	Links = [];
	for i in range(len(Nodes)):
		for j in range(len(Nodes)):
			if i == j:
				continue
			dis = Node_distance.Dis.cal_dis(Nodes[i], Nodes[j])
			#dis = math.sqrt((Nodes[i].x_pos - Nodes[j].x_pos)**2+(Nodes[i].y_pos - Nodes[j].y_pos)**2)
			# node interference range
			node_ir = math.sqrt(Nodes[i].pt * Nodes[i].gain * Nodes[j].gain * Nodes[i].height**2\
								 * Nodes[j].height**2 / Nodes[j].CS_th) * path_loss
			if node_ir >= dis:
				Links.append(Mesh_link.Link(Nodes[i], Nodes[j]))
				Nodes[i].out_neighbours.append(j)
				Nodes[j].in_neighbours.append(i)

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
			for j in Nodes[i].out_neighbours:
				if Nodes[j].is_gateway() == 1:
					break
				if j in vis:
					continue
				queue.append(j)
				vis.append(j)
		Nodes[i].min_hop_count = mhc

	# calculate rank for each link
	for i in range(len(Links)):
		link_neighbours = len(Links[i].node1.out_neighbours) + len(Links[i].node2.in_neighbours)
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

	for it in range(len(des_links_list)):
		SD = np.zeros(12)
		SS = np.zeros(12)
		SE = np.zeros(12)
		
		node_s = des_links_list[it].node1
		node_t = des_links_list[it].node2
		D_st = Node_distance.Dis.cal_dis(node_s, node_t)
		Prt  = node_s.pt * node_s.gain * node_t.gain / D_st**2
		# calculate SD, SS, SE score function
		for omega in range(12):
			if it != 0:
				for j in range(it):
					delta_omega = abs(omega - des_links_list[j].channel)
					node_p = des_links_list[j].node1
					node_q = des_links_list[j].node2
					D_pt = Node_distance.Dis.cal_dis(node_p, node_t)
					D_sq = Node_distance.Dis.cal_dis(node_s, node_q)
					# claculate how current link interferenced by other links
					if node_p.index in node_t.in_neighbours:
						Prti = node_p.pt * node_p.gain * node_t.gain / D_pt**2
						SD[omega] += Prti / Prt * G[delta_omega]

					# calculate how current link interferences other assigned links 
					if node_q.index in node s.out_neighbours:
						Prtj = node_s.pt * node_s.gain * node_q.gain / D_sq**2
						SS[omega] += pow(abs(Prtj / Prt - 1) * G[delta_omega], Minkowski)

				SS = [x**(1/Minkowski) for x in SS]

			# calculate how current link interferences other unassigned links 
			if it != len(des_links_list)-1:
				for j in range(it+1, len(des_links_list)):
					node_q = des_links_list[j].node2
					D_sq = Node_distance.Dis.cal_dis(node_s, node_q)
					if node_q.index in node s.out_neighbours:
						SE[omega] += node_q.gain/D_sq**2 * F[omega]

		# call set_channel function
		des_links_list[it].set_channel(SD, SS, SE)
		


if __name__ = '__main__':
	main()