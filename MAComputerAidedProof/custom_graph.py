import os
import pickle

import graph_coloring as gc
import networkx as nx
from matplotlib import pyplot as plt
from networkx.algorithms import isomorphism


class CustomGraph(nx.Graph):

    def __init__(self, *args, **kwargs):
        super(CustomGraph, self).__init__(*args, **kwargs)
        self.name = kwargs.get('name', '')
        self.edge_numbers = kwargs.get('edge_numbers', [])
        self.graph_numbers = kwargs.get('graph_numbers', [])
        self.possible_precolorings = kwargs.get('possible_precolorings', [])

    # Determines whether the graph contains a triangle
    def has_triangle(self):
        return any(nx.triangles(self).values())

    # Determines whether the graph contains an induced diamond
    def has_diamond(self):
        diamond = nx.diamond_graph()
        gm = isomorphism.GraphMatcher(self, diamond)
        has_a_diamond = gm.subgraph_is_isomorphic()

        return has_a_diamond

    # Determines whether the graph contains a K4
    def has_k4(self):
        k4 = nx.complete_graph(4)
        gm = isomorphism.GraphMatcher(self, k4)
        has_a_k4 = gm.subgraph_is_isomorphic()

        return has_a_k4

    # Determines whether the graph contains an induced path of length 6
    def has_induced_p6(self):
        p6 = nx.path_graph(6)
        gm = isomorphism.GraphMatcher(self, p6)
        has_a_p6 = gm.subgraph_is_isomorphic()

        return has_a_p6

    # Determines whether the graph is (P6, triangle)-free
    def is_p6_triangle_free(self):
        return not self.has_triangle() and not self.has_induced_p6()

    # Determines whether the graph is (P6, diamond, K4)-free
    def is_p6_diamond_k4_free(self):
        return not self.has_induced_p6() and not self.has_diamond() and not self.has_k4()

    # Groups the nodes by the first character of their name and returns them in a dictionary
    def get_nodes_by_initial(self):
        node_dict = {}
        for node in self.nodes():
            initial = node[0]
            if initial not in node_dict:
                node_dict[initial] = set()
            node_dict[initial].add(node)
        return node_dict

    # Determines whether a given coloring for the graph is proper
    def is_possible_coloring(self, coloring):
        for node, color in coloring.items():
            if any(coloring[neighbor] == color for neighbor in nx.neighbors(self, node) if neighbor in coloring):
                return False
        return True

    # Determines, whether applying the precoloring to the graph and updating all color lists decomposes the last cycle in the graph.
    def decomposed_by_precoloring(self, precoloring, nodes_per_cycle):
        new_color_lists = {node: [1, 2, 3] for node in self.nodes()}
        color_lists = gc.precolor(self, new_color_lists, precoloring)
        coloring = gc.get_coloring_from_color_lists(color_lists)

        if self.number_of_nodes() - nodes_per_cycle < len(coloring) or len(coloring) == 0:
            return True, coloring
        return False, coloring

    # Determines, whether applying the precoloring to the graph and updating all color lists while regarding the color restriction, decomposes the last C5 in the graph.
    def decomposed_by_precoloring_with_color_restriction(self, precoloring, nodes_per_cycle):
        new_color_lists = {node: [1, 2, 3] for node in self.nodes()}
        color_lists = gc.precolor_with_color_restriction(self, new_color_lists, precoloring)
        coloring = gc.get_coloring_from_color_lists(color_lists)

        if self.number_of_nodes() - nodes_per_cycle < len(coloring) or len(coloring) == 0:
            return True, coloring
        return False, coloring

    # Save the graph in a pickle file
    def save_to_pickle(self, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    # Load a graph from a pickle file
    @classmethod
    def load_from_pickle(cls, file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    # Draw the graph and save the figure in a file
    def draw_and_save(self, file_path, coloring):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        color_map = {
            1: 'red',
            2: 'blue',
            3: 'green'
        }
        node_colors = [color_map.get(coloring.get(node, 0), 'gray') for node in self.nodes()]

        pos = nx.circular_layout(self)
        plt.figure(figsize=(8, 8))
        nx.draw(self, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=3000, font_size=15, font_weight='bold')
        plt.savefig(file_path)
        plt.close()

    @classmethod
    def from_networkx_graph(cls, nx_graph, name, edge_numbers, graph_numbers, possible_precolorings):
        custom_graph = cls()
        custom_graph.add_nodes_from(nx_graph.nodes(data=True))
        custom_graph.add_edges_from(nx_graph.edges(data=True))

        custom_graph.name = name
        custom_graph.edge_numbers = edge_numbers
        custom_graph.graph_numbers = graph_numbers
        custom_graph.possible_precolorings = possible_precolorings
        return custom_graph
