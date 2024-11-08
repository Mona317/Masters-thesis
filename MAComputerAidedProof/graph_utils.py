import itertools
import networkx as nx
from networkx import isomorphism
import concurrent.futures
from pathlib import Path

import custom_graph
import graph_io as gio


# Generates all possible sets of edges of a given size between two cycles. When nodes_per_cycle = 5, then the method also considers the incidence constraints.
def generate_all_possible_edgesets(g1, g2, size, nodes_per_cycle):
    possible_edges = list(itertools.product(g1.nodes(), g2.nodes()))

    possible_edge_subsets = []
    combinations = itertools.combinations(possible_edges, size)
    for edge_subset in combinations:
        if (nodes_per_cycle != 5) or is_possible_edge_subset(nx.compose(g1, g2), edge_subset):
            possible_edge_subsets.append(edge_subset)

    return possible_edge_subsets


# Determines for each node, to how many edges it is incident.
def calculate_incidence(edge_subset):
    incidence = {}
    for u, v in edge_subset:
        incidence[u] = incidence.get(u, 0) + 1
        incidence[v] = incidence.get(v, 0) + 1
    return incidence


# Checks whether the following holds for each node in g:
# 1. it is incident to at most 2 edges
# 2. if it is incident to 0 edges, then each of its neighbors is incident to exactly 2 edges.
def check_incidence_constraints(g, incidence):
    for node in g.nodes():
        node_incidence = incidence.get(node, 0)
        if node_incidence > 2:
            return False
        if node_incidence == 0:
            neighbors = list(g.neighbors(node))
            if any(incidence.get(neighbor, 0) != 2 for neighbor in neighbors):
                return False
    return True


# Determines, whether a set of edges can connect two C5s, only considering the incidence constraints.
def is_possible_edge_subset(g, edge_subset):
    incidence = calculate_incidence(edge_subset)
    return check_incidence_constraints(g, incidence)


# Combines two graphs and a set of edges
def compose_graphs(g1, g2, edgesets):
    graphs = []
    for edgeset in edgesets:
        g = nx.compose(g1, g2)
        g.add_edges_from(edgeset)
        graphs.append(g)
    return graphs


# Checks for Isomorphisms where each cycle is mapped onto itself and returns only one representation for each isomorphism class
def filter_isomorphisms_with_cycle_to_cycle_mapping(graphs):
    filtered_graphs = []

    for graph1 in graphs:
        node_groups = graph1.get_nodes_by_initial()
        found = False
        for graph2 in filtered_graphs:
            gm = isomorphism.GraphMatcher(graph1, graph2)

            for mapping in gm.isomorphisms_iter():
                valid_mapping = True

                for char, nodes_set in node_groups.items():
                    mapped_nodes = {mapping[node] for node in nodes_set if node in mapping}

                    if not all(mapped_node in nodes_set for mapped_node in mapped_nodes):
                        valid_mapping = False
                        break

                if valid_mapping:
                    found = True
                    break
            if found:
                break

        if not found:
            filtered_graphs.append(graph1)

    return filtered_graphs


# Gets the list of all graphs, that represent two C5s with all possible connections, from the results folder
def get_connections_2c5s():
    connections_2_c5s = {}
    for i in range(5, 11):
        path = 'results/c5s/' + '2_c5s/' + str(i) + '_connecting_edges'
        if Path(path).exists():
            connections_2_c5s[str(i)] = gio.read_graph_files(path)

    return connections_2_c5s


# Gets the list of all graphs, that represent two triangle with all possible connections, from the results folder
def get_connections_2c3s():
    connections_2_c3s = {}
    for i in range(1, 4):
        path = 'results/c3s/' + '2_c3s/' + str(i) + '_connecting_edges'
        if Path(path).exists():
            connections_2_c3s[str(i)] = gio.read_graph_files(path)

    return connections_2_c3s


# Gets the list of all graphs, that represent (k - 1) cycles with all possible connections, from the results folder
def get_connections_last_iteration(k, nodes_per_cycle):
    if k == 3:
        if nodes_per_cycle == 3:
            connections_last_iteration = get_connections_2c3s()
        elif nodes_per_cycle == 5:
            connections_last_iteration = get_connections_2c5s()
        else:
            return {}
    else:
        connections_last_iteration = {}
        subfolders = gio.get_subfolders_with_suffix('results/c' + str(nodes_per_cycle) + 's/' + str(k - 1) + '_c' + str(nodes_per_cycle) + 's_with_precoloring', '_connecting_edges')
        for (subfolder, connecting_edges) in subfolders:
            connections_last_iteration[connecting_edges] = gio.read_graph_files(subfolder)

    return connections_last_iteration


# Gets the list of all graphs, that represent (k - 1) cycles connected by edges, from the results folder.
# Here only one representative for each set of graphs, that are isomorphic and the isomorphism sends each cycle onto the same cycle, is given.
def get_unique_connections_last_iteration(k, nodes_per_cycle):
    unique_connections_last_iteration = {}
    if k == 3:
        path = 'results/c' + str(nodes_per_cycle) + 's/' + str(k - 1) + '_c' + str(nodes_per_cycle) + 's_unique_by_automorphisms'
    else:
        path = 'results/c' + str(nodes_per_cycle) + 's/' + str(k - 1) + '_c' + str(nodes_per_cycle) + 's_with_precoloring_unique_by_automorphisms'
    subfolders = gio.get_subfolders_with_suffix(path, '_connecting_edges')
    for (subfolder, connecting_edges) in subfolders:
        unique_connections_last_iteration[connecting_edges] = gio.read_graph_files(subfolder)

    return unique_connections_last_iteration


# Combines the three input graphs to one graph that consists of k C5s in the following way:
# graph_last_iteration_1 and graph_last_iteration_2 consist of k-1 C5s, graph_connection_2_c5s consists of 2 C5s.
# In the new graph, the edges in graph_last_iteration_1 represent the edges between the first k-1 C5s in the new graph.
# The edges in graph_last_iteration_2 represent the edges between the first k-2 C5s with the k'th C5 in the new graph.
# The edges in graph_connection_2_c5s represent the edges between the k-1'th C5s with the k'th C5 in the new graph.
def combine_graph_from_last_iteration(graph_last_iteration_1, graph_last_iteration_2, graph_connection_2_cycles, nodes_per_cycle):

    g1 = graph_last_iteration_1.copy()
    last_cycle_node_name = max([node[0] for node in graph_last_iteration_2])
    current_position = ord(last_cycle_node_name) - ord('a')
    new_position = (current_position + 1) % 26
    new_cycle_name = chr(new_position + ord('a'))

    g2_node_mapping = {node: node for node in graph_last_iteration_2.nodes() if node[0] != last_cycle_node_name}
    g2_node_mapping.update({node: new_cycle_name + node[1:] for node in graph_last_iteration_2.nodes() if node[0] == last_cycle_node_name})
    g2 = nx.relabel_nodes(graph_last_iteration_2, g2_node_mapping, True)

    g3_node_mapping = {node: last_cycle_node_name + node[1:] for node in graph_connection_2_cycles.nodes() if node[0] == 'u'}
    g3_node_mapping.update({node: new_cycle_name + node[1:] for node in graph_connection_2_cycles.nodes() if node[0] == 'v'})
    g3 = nx.relabel_nodes(graph_connection_2_cycles, g3_node_mapping, True)

    combined_graph = nx.compose_all([g1, g2, g3])

    n = combined_graph.number_of_nodes() // nodes_per_cycle

    edge_numbers = graph_last_iteration_1.edge_numbers.copy()
    if len(graph_last_iteration_2.edge_numbers) <= 1:
        edge_numbers.extend(graph_last_iteration_2.edge_numbers)
    else:
        edge_numbers.extend(graph_last_iteration_2.edge_numbers[((n - 2) * (n - 3)) // 2:])
    edge_numbers.append(graph_connection_2_cycles.edge_numbers[0])

    graph_numbers = graph_last_iteration_1.graph_numbers.copy()
    if len(graph_last_iteration_2.graph_numbers) <= 1:
        graph_numbers.extend(graph_last_iteration_2.graph_numbers)
    else:
        graph_numbers.extend(graph_last_iteration_2.graph_numbers[((n - 2) * (n - 3)) // 2:])
    graph_numbers.append(graph_connection_2_cycles.graph_numbers[0])

    possible_precolorings = graph_last_iteration_1.possible_precolorings.copy()

    name = 'graph' + str(graph_numbers[0])
    for graph_number in graph_numbers[1:]:
        name += '_' + str(graph_number)

    new_graph = custom_graph.CustomGraph.from_networkx_graph(combined_graph, name, edge_numbers, graph_numbers, possible_precolorings)
    return new_graph


# Parallelizes the execution of the method for all given inputs
def run_parallel(method, inputs):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(method, inputs)
