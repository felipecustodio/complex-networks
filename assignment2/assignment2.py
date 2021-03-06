#!/bin/usr/env python3
# -*- coding: utf-8 -*-

"""
Dynamical Processes in Complex Networks
University of Sao Paulo
Professor Francisco Aparecido Rodrigues

Students:
Felipe Scrochio Custódio - 9442688
Gabriel Henrique Scalici - 9292970


Assignment 2 - Correlation and Communities
"""

import networkx as nx
import igraph as ig

from itertools import *

import numpy as np
from matplotlib import pyplot as pp
import seaborn as sns
from subprocess import call

from sklearn.metrics import normalized_mutual_info_score

# plot colors
colors = ["#1abc9c", "#2ecc71", "#3498db", "#f1c40f", "#e67e22", "#e74c3c", "#2c3e50"]


def pearson(x, y):
    n = len(x)
    sum_x = float(sum(x))
    sum_y = float(sum(y))
    sum_x_sq = sum(map(lambda x: pow(x, 2), x))
    sum_y_sq = sum(map(lambda x: pow(x, 2), y))
    psum = sum(map(lambda x, y: x * y, x, y))
    num = psum - (sum_x * sum_y / n)
    den = pow((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n), 0.5)
    if den == 0: return 0
    return num / den


def giant_component(graph):
    return nx.Graph(max(nx.connected_component_subgraphs(graph), key=len))


def read_graph(filename):
    graph = nx.Graph()
    with open(filename, 'rb') as f:
        for line in f:
            nodes = line.split()
            graph.add_edge(nodes[0], nodes[1])
    graph = graph.to_undirected()
    return giant_component(graph)


def nx_to_ig(graph):
    g = ig.Graph.TupleList(graph.edges(), directed=False)
    return g


def assortativity(graphs):
    print("ASSORTATIVITY")
    for name, graph in graphs.items():
        assortativity = nx.degree_assortativity_coefficient(graph)
        print("%s: %.4f" % (name, assortativity))


def k_x_knn(graphs):
    print("K X KNN")
    i = 0
    for name, graph in graphs.items():
        print(name)

        degrees = list(graph.degree().values())
        knn_degrees = list((nx.average_degree_connectivity(graph)).values())
        knn_vertex = list((nx.average_neighbor_degree(graph)).values())
        k = range(1, len(knn_degrees) + 1)

        # prepare plotting area
        sns.set()
        fig = pp.figure()
        ax1 = fig.add_subplot(111, label="k(x) x knn(x)")
        ax2 = fig.add_subplot(111, label="knn(k)", frame_on=False)

        # knn(x) - scatter
        plot1 = ax1.scatter(degrees, knn_vertex, s=10, color=colors[i], marker='o', label="k(x) x knn(x)")
        ax1.set_xlabel("k(x)")
        ax1.set_ylabel("knn(x)")
        ax1.tick_params(axis='x')
        ax1.tick_params(axis='y')
        # knn(k) - line
        plot2, = ax2.plot(k, knn_degrees, c=colors[i + 1], label="knn(k)")
        ax2.xaxis.tick_top()
        ax2.yaxis.tick_right()
        ax2.set_xlabel("k")
        ax2.set_ylabel("knn(k)")
        ax2.xaxis.set_label_position('top')
        ax2.yaxis.set_label_position('right')
        ax2.tick_params(axis='x')
        ax2.tick_params(axis='y')

        # plot
        fig.tight_layout()
        pp.figlegend((plot1, plot2), ('k(x) x knn(x)', 'knn(k)'), loc='lower right')
        fig.subplots_adjust(top=0.85, bottom=0.15)
        pp.suptitle("k x knn - %s" % name)
        pp.grid(False)

        pp.savefig('plots/' + name + "-kxknn.png", bbox_inches='tight')
        pp.clf()
        i += 1

        # correlation k(x) x knn(x)
        correlation = pearson(graph.degree().values(), knn_vertex)
        print("pearson correlation coefficient: %.4f" % correlation)


def modularities(graphs):
    print("MODULARITIES")

    for name, graph in graphs.items():
        print(name)
        # convert to igraph
        g = nx_to_ig(graph)
        # edge betweenness centrality
        community = g.community_edge_betweenness(directed=False).as_clustering()
        print("edge betweenness centrality: %.4f" % (community.modularity))
        # fast-greedy
        community = g.community_fastgreedy().as_clustering()
        print("fast greedy: %.4f" % (community.modularity))
        # eigenvectors of matrices
        community = g.community_leading_eigenvector()
        print("eigenvectors of matrices: %.4f" % (community.modularity))
        # walktrap
        community = g.community_walktrap().as_clustering()
        print("walktrap: %.4f" % (community.modularity))
        print("\n")


def plot_modularity_evolution(graphs):
    for name, graph in graphs.items():
        print(name)
        # convert
        g = nx_to_ig(graph)

        # fast-greedy
        evolution = g.community_fastgreedy()
        count = evolution.optimal_count

        # aux
        count = count - 1
        tam = len(g.vs)

        # axis
        value_x = range(tam, count, -1)
        value_y = np.zeros(len(value_x))

        list_values_y = range(len(value_y))
        for i in list_values_y:
            value_y[i] = evolution.as_clustering(n=value_x[i]).modularity

        # reverse
        value_x = value_x[::-1]

        # plot
        sns.set()
        pp.plot(value_x, value_y, color=colors[0], marker='o')
        pp.title("Modularity Evolution - " + name)
        pp.grid(False)
        pp.ylabel("Modularity")
        pp.xlabel("Step")
        pp.savefig('plots/' + name + '-mod_evolution.png')
        pp.clf()


def communities():
    print("COMMUNITY DETECTION")

    # initialize NMI vectors
    nmi = {}
    nmi["edge_bet"] = []
    nmi["fastgreedy"] = []
    nmi["eigenvector"] = []
    nmi["walktrap"] = []

    # varying mu from 0.1 to 1.0
    mu = np.arange(0.1, 1.1, 0.1)
    for i in mu:
        print("Running for mu = %.1f" % i)

        # run package / generate communities
        call(['./binary_networks/benchmark', '-N', '300', '-k', '10', '-maxk', '30', '-mu', str(i)])

        network = open('./network.dat', 'rb')
        # read generated graph
        g = ig.Graph.Read_Edgelist(network, directed=False)
        g.delete_vertices(0)
        g.simplify()
        # the membership vector should contain the community id of each vertex
        # read generated memberships vector
        memberships = []
        mems = open('./community.dat')
        for line in mems:
            memberships.append(int(line.split()[1]))  # append community id

        # apply detection algorithms and get new memberships vectors
        detection_edge_bet = g.community_edge_betweenness(directed=False).as_clustering().membership
        detection_fastgreedy = g.community_fastgreedy().as_clustering().membership
        detection_eigenvector = g.community_leading_eigenvector().membership
        detection_walktrap = g.community_walktrap().as_clustering().membership

        # NMI
        nmi["edge_bet"].append(normalized_mutual_info_score(memberships, detection_edge_bet))
        nmi["fastgreedy"].append(normalized_mutual_info_score(memberships, detection_fastgreedy))
        nmi["eigenvector"].append(normalized_mutual_info_score(memberships, detection_eigenvector))
        nmi["walktrap"].append(normalized_mutual_info_score(memberships, detection_walktrap))

    # plot
    sns.set()

    pp.plot(mu, nmi["edge_bet"], color=colors[0], linestyle='solid', marker='o', label='edge betweenness centrality')
    pp.plot(mu, nmi["fastgreedy"], color=colors[3], linestyle='solid', marker='o', label='fastgreedy')
    pp.plot(mu, nmi["eigenvector"], color=colors[5], linestyle='solid', marker='o', label='eigenvetor matrices')
    pp.plot(mu, nmi["walktrap"], color=colors[6], linestyle='solid', marker='o', label='walktrap')

    pp.title("NMI")
    pp.ylabel("NMI")
    pp.xlabel("Mixing parameter µ")
    pp.legend(loc='lower left', ncol=1)
    pp.grid(False)

    pp.savefig('plots/nmi.png')


# read networks
graphs = {}
graphs["Euroroad"] = read_graph("./networks/euroroad.txt")
graphs["Hamster"] = read_graph("./networks/hamster.txt")
graphs["Airports"] = read_graph("./networks/USairports.txt")
graphs["Cortical Human"] = read_graph("./networks/cortical-human.txt")
graphs["Cortical Cat"] = read_graph("./networks/cortical-cat.txt")
graphs["Cortical Monkey"] = read_graph("./networks/cortical-monkey.txt")

# 1
assortativity(graphs)
# 2
k_x_knn(graphs)
# 3, 6
# modularities(graphs)
# 5
plot_modularity_evolution(graphs)
# 7
communities()
print("done")
