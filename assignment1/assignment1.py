#!/bin/usr/env python3
# -*- coding: utf-8 -*-

'''
Dynamical Processes in Complex Networks
University of Sao Paulo
Professor Francisco Aparecido Rodrigues

Students: 
Felipe Scrochio Custódio - 9442688
Gabriel Henrique Scalici - 9292970


Assignment 1 - Complex Networks caracterization
'''

import networkx as nx
import numpy as np
import powerlaw
from matplotlib import pyplot as pl

def read_graph(filename):
    graph = nx.Graph()
    with open(filename, 'rb') as f:
        for line in f:
            nodes = line.split()
            graph.add_edge(nodes[0], nodes[1])
    return graph


def draw_graph(graph):
    nx.draw(graph)
    # pl.savefig(filename)
    pl.show()


def stat_moment(graph, moment):
    measure = 0
    for node in graph.nodes_iter():
        measure += graph.degree(node) ** moment
    return measure / graph.number_of_nodes()


def giant_component(graph):
    return nx.Graph(max(nx.connected_component_subgraphs(graph), key=len))


def degree_distribution(graph):
    degrees = {}
    for node in graph.nodes_iter():
        degree = graph.degree(node)
        if degree not in degrees:
            degrees[degree] = 0
        degrees[degree] += 1
    distribution = sorted(degrees.items())
    return distribution


def is_scale_free(graph):
    distribution = np.asarray(degree_distribution(graph))
    # fit = powerlaw.Fit(distribution)]
    fit = powerlaw.Fit(distribution)
    exponent = fit.power_law.alpha
    if (exponent >= 2 and exponent <= 3):
        return True
    else:
        return False


def centralities(graph):
    betweenness_centrality = nx.betweenness_centrality(graph)
    closeness_centrality = nx.closeness_centrality(graph)
    eigenvector_centrality = nx.eigenvector_centrality(graph)
    pagerank = nx.pagerank(graph)




def average_degree(graph):
    degrees = graph.degree().values()
    average = sum(degrees)/len(degrees)
    return average


def measures(graph):
    print("MEDIDAS")
    print("Número de vértices: ", len(graph))
    print("Grau médio: ", average_degree(graph))
    print("Segundo momento da distribuição do grau: ", stat_moment(graph, 2))
    print("Média do coef. de aglomeração local: ", nx.average_clustering(graph))
    print("Transitividade: ", nx.transitivity(graph))
    print("Média dos menores caminhos: ", nx.average_shortest_path_length(graph))
    print("Diâmetro: ", nx.diameter(graph))


def histograms(graphs):
    # distribuição dos menores caminhos
    
    # encontrar todos os menores caminhos para todos os grafos
    paths = []
    for graph in graphs:
        paths.append(nx.shortest_path(graph))
    
    # plotar distribuições em escala log
    plot = plt.subplot()
    graph.loglog(paths[0], color='#D45C7E', marker='None', label='euroroad')
    graph.loglog(paths[1], color='#C9533E', marker='None', label='hamster')
    graph.loglog(paths[2], color='#45415C', marker='None', label='powergrid')
    graph.loglog(paths[3], color='#DC7B28', marker='None', label='airports')
    
    # configurar visual do gráfico
    graph.spines['right'].set_visible(False)
    graph.spines['top'].set_visible(False)
    graph.yaxis.set_ticks_position('left')
    graph.xaxis.set_ticks_position('bottom')
    plt.legend()
    plt.subplots_adjust(hspace=0.5)
    
    # exibir
    plt.show()







def pearson(measures):
    pass
    # scatter plots


def process_graph(graph):
    pass


# read networks
euroroad = read_graph("./networks/euroroad.txt")
hamster = read_graph("./networks/hamster.txt")
powergrid = read_graph("./networks/us-powergrid.txt")
airports = read_graph("./networks/us-airports.txt")

graphs = []
graphs.append(euroroad)
graphs.append(hamster)
graphs.append(powergrid)
graphs.append(airports)

# get biggest component
giants = {}
for graph in graphs:
    giants[graph] = giant_component(graph)


histograms(giants)

# measures
# print("---------------------")
# print("EuroRoad")
# measures(giants[euroroad])
# print("---------------------")

# print("Hamster")
# measures(giants[hamster])
# print("---------------------")

# print("Powergrid")
# measures(giants[powergrid])
# print("---------------------")

# print("Airports")
# measures(giants[airports])
# print("---------------------")
