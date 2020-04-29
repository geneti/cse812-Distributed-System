import os
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import math
import copy

import Gaussian_2d, NodeDistribution, Mesh_node, Mesh_link
import node_distance, IR
import utils
import main
import plot_graph

# hyper parameters
# links interference range list from 0 to 11
G = [2, 1.125, 0.75, 0.375, 0.125, 0, 0, 0, 0, 0, 0, 0]
F = [0, 0, 0.0009, 0.0175, 0.1295, 0.3521, 0.3521, 0.1295, 0.0175, 0.0009, 0, 0]
Minkowski = 2
interference_ceiling = 10**8  # when the distance between two links is 0, we set a large constant value here


def base_channel_assignment(Nodes, Links, C_Links, argv, fni_all=False):
	fni_list = []
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
		link_neighbours = len(Links[i].node1.out_neighbours) + len(
			Links[i].node2.in_neighbours)
		link_min_hop_count = min(Links[i].node1.min_hop_count, Links[i].node2.min_hop_count)
		link_distance = Links[i].distance
		Links[i].rank = link_neighbours * link_distance**2 * Links[i].node2.Rx_th / (link_min_hop_count * \
			Links[i].node1.pt * Links[i].node1.gain * Links[i].node2.gain)
	print('rank list generated of length: ', len(Links))

	# create deep copy of links list and sort in descending order by rank
	def take_rank(elem):
		# elem is a link object
		return elem.rank

	des_links_list = Links
	des_links_list.sort(key = take_rank)

	for it in range(len(des_links_list)):
		print(f"\r\t[{it+1}/{len(des_links_list)}]", end='')
		Score = np.zeros(12)
		node_s = des_links_list[it].node1
		node_t = des_links_list[it].node2
		# calculate score for each possible channel
		for omega in range(12):
			if it != 0:
				for j in range(it):
					node_p = des_links_list[j].node1
					node_q = des_links_list[j].node2
					D_pt = node_distance.Dis.cal_dis(node_p, node_t)
					D_sq = node_distance.Dis.cal_dis(node_s, node_q)
					D_sp = node_distance.Dis.cal_dis(node_s, node_p)
					D_tq = node_distance.Dis.cal_dis(node_t, node_q)

					Min_dis = min(min(D_pt, D_sp), min(D_sq, D_tq))
					if Min_dis == D_pt:
						nir = IR.Node_IR(node_p, node_t, argv.path_loss)
						NIR = nir.ir
					elif Min_dis == D_sp:
						# when calculate the IR for 2 transmitters, choose the bigger one
						nir1 = IR.Node_IR(node_p, node_s, argv.path_loss)
						nir2 = IR.Node_IR(node_s, node_p, argv.path_loss)
						NIR = max(nir1.ir, nir2.ir)
					elif Min_dis == D_sq:
						nir = IR.Node_IR(node_s, node_q, argv.path_loss)
						NIR = nir.ir
					elif Min_dis == D_tq:
						# when calculate the IR for 2 transmitters, choose the bigger one
						nir1 = IR.Node_IR(node_t, node_q, argv.path_loss)
						nir2 = IR.Node_IR(node_q, node_t, argv.path_loss)
						NIR = max(nir1.ir, nir2.ir)

					# score the current possible channel
					# assume the busy idle ratio for 2 links is the average
					bil = (des_links_list[j].busy_idle_ratio + des_links_list[it].busy_idle_ratio) / 2
					if Min_dis == 0:
						Score[omega] += interference_ceiling
					elif Min_dis <= NIR:
						Score[omega] += NIR / Min_dis * bil

		# call set_channel function
		des_links_list[it].set_channel_base(Score)

		if argv.plot_steps:
			fig_path = os.path.join(argv.fig_root, f"n{len(Nodes)}",
									f"step_{it:04d}.png")
			plot_graph.plot_graph(Nodes, Links, fig_path=fig_path)
			print(f'Saving to {fig_path} ')

		if fni_all:
			fni = utils.cal_fni(C_Links, argv.inter_range)
			fni_list.append(fni)

	if len(fni_list) == 0:
		fni = utils.cal_fni(C_Links, argv.inter_range)
		fni_list.append(fni)
		print()

	return fni_list


def test_base_method(argv):
	Ns = list(range(argv.min_node, argv.max_node + 1))
	fni_list = []

	if argv.plot_special_n3 or argv.plot_special_n4:
		Ns = [0]
	elif argv.plot_steps and len(Ns) > 1:
		raise Exception(
			"min_node and max_node should equal if you want to plot steps")

	for num in Ns:
		# generate graph
		# generate location matrix
		if argv.plot_special_n3:
			LM = pd.DataFrame([[20, 20], [20, 10], [10, 20]])
		elif argv.plot_special_n4:
			LM = pd.DataFrame([[20, 20], [20, 10], [10, 20], [10, 10]])
		else:
			t = NodeDistribution.location_matrix(argv.width, argv.height, num,
												'Random')
			LM = t.generate()
		# LM = pd.DataFrame([[20, 20], [20, 10], [10, 20], [10, 10]])
		Nodes, Links = utils.gen_graph(LM, argv.gateway_prob, argv.path_loss)

		print(f"Processing {len(Nodes)} nodes")
		C_Links = utils.gen_conflict_graph(Links, argv.inter_range)
		print('link list generated')

		if len(Ns) == 1:
			fni_list = base_channel_assignment(Nodes,
											Links,
											C_Links,
											argv,
											fni_all=True)
		else:
			fni_list_local = base_channel_assignment(Nodes, Links, C_Links,
													argv)
			fni_list.append(fni_list_local[-1])

	fig, ax = plt.subplots()

	if len(Ns) == 1:
		ax.plot(list(range(1, len(Links) + 1)), fni_list)

		ax.set_xlabel('Number of Links with channel assigned')
		ax.set_ylabel('Frictional Network Interference')
		# ax.set_yscale('log')
		fig_path = os.path.join(argv.fig_root, "base_fni_nlink.png")
	else:
		ax.plot(Ns, fni_list)

		ax.set_xlabel('Number of Nodes')
		ax.set_ylabel('Frictional Network Interference')
		# ax.set_yscale('log')
		fig_path = os.path.join(argv.fig_root, "base_fni_n.png")

	print(f'Saving to {fig_path}')
	plt.savefig(fig_path, format='png', bbox_inches='tight')
	print()


if __name__ == '__main__':
	argv = main.parse_arguments([])
	test_base_method(argv)
