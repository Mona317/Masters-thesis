import networkx as nx

import graph_io as gio
import graph_utils as gu
import custom_graph
import graph_coloring as gc


# Generates two C5s and determines all possible combinations of edges, that can run between the two C5s. For every resulting graph, it is checked, whether it is (P6, triangle)-free. The (P6, triangle)-free graphs are then saved to the results folder.
def find_connections_2_c5s():
    # Counts the number of resulting graphs, to give them unique names
    graph_counter = 0
    for edge_number in range(5, 11):
        # Generates 2 C5s
        g1 = nx.cycle_graph(5)
        g2 = nx.cycle_graph(5)

        g1 = nx.relabel_nodes(g1, {num: 'u' + str(num) for num in list(g1)})
        g2 = nx.relabel_nodes(g2, {num: 'v' + str(num) for num in list(g2)})

        # Determines all possible combinations of edges, that can run between the two C5s
        possible_edgesets = gu.generate_all_possible_edgesets(g1, g2, edge_number, 5)

        # Combines the C5s and the edges to a new Graph
        nx_graphs = gu.compose_graphs(g1, g2, possible_edgesets)

        # Checks for each graph, whether it is (P6, triangle)-free
        p6_triangle_free_graphs = []
        for nx_graph in nx_graphs:
            graph = custom_graph.CustomGraph.from_networkx_graph(nx_graph, 'graph' + str(graph_counter), [edge_number], [graph_counter], set())
            if graph.is_p6_triangle_free():
                p6_triangle_free_graphs.append(graph)
                graph_counter += 1

        # Saves the graphs and their plots
        gio.save_graphs_in_directory(p6_triangle_free_graphs,
                                     'results/c5s/2_c5s/' + str(edge_number) + '_connecting_edges')
        gio.save_graph_plots_in_directory(p6_triangle_free_graphs,
                                          'results/c5s/2_c5s/' + str(edge_number) + '_connecting_edges_plots')


# Generates two triangles and determines all possible combinations of edges, that can run between the two triangles. For every resulting graph, it is checked, whether it is (P6, K4, diamong)-free. The (P6, triangle)-free graphs are then saved to the results folder.
def find_connections_2_c3s():
    # Counts the number of resulting graphs, to give them unique names
    graph_counter = 0
    for edge_number in range(1, 4):
        # Generates 2 triangles
        g1 = nx.cycle_graph(3)
        g2 = nx.cycle_graph(3)

        g1 = nx.relabel_nodes(g1, {num: 'u' + str(num) for num in list(g1)})
        g2 = nx.relabel_nodes(g2, {num: 'v' + str(num) for num in list(g2)})

        # Determines all possible combinations of edges, that can run between the two triangles
        possible_edgesets = gu.generate_all_possible_edgesets(g1, g2, edge_number, 3)

        # Combines the triangles and the edges to a new Graph
        nx_graphs = gu.compose_graphs(g1, g2, possible_edgesets)

        # Checks for each graph, whether it is (P6, k4, diamond)-free
        p6_k4_diamond_free_graphs = []
        for nx_graph in nx_graphs:
            graph = custom_graph.CustomGraph.from_networkx_graph(nx_graph, 'graph' + str(graph_counter), [edge_number], [graph_counter], set())
            if graph.is_p6_diamond_k4_free():
                p6_k4_diamond_free_graphs.append(graph)
                graph_counter += 1

        # Saves the graphs and their plots
        gio.save_graphs_in_directory(p6_k4_diamond_free_graphs,
                                     'results/c3s/2_c3s/' + str(edge_number) + '_connecting_edges')
        gio.save_graph_plots_in_directory(p6_k4_diamond_free_graphs,
                                          'results/c3s/2_c3s/' + str(edge_number) + '_connecting_edges_plots')


# Runs through the list of connections between two C5s and only saves one representative for each set of graphs, in which every graph is isomorphic to each other with an isomorphism that sends each C5 onto itself.
def find_connections_2_c5s_with_filtered_automorphisms():
    for i in range(5, 11):
        directory_name = 'results/c5s/2_c5s/' + str(i) + '_connecting_edges'
        new_directory_name = 'results/c5s/2_c5s_unique_by_automorphisms/' + str(i) + '_connecting_edges'

        graphs = gio.read_graph_files(directory_name)
        unique_graphs = gu.filter_isomorphisms_with_cycle_to_cycle_mapping(graphs)

        gio.save_graphs_in_directory(unique_graphs, new_directory_name)


# Runs through the list of connections between two triangles and only saves one representative for each set of graphs, in which every graph is isomorphic to each other with an isomorphism that sends each triangle onto itself.
def find_connections_2_c3s_with_filtered_automorphisms():
    for i in range(1, 4):
        directory_name = 'results/c3s/2_c3s/' + str(i) + '_connecting_edges'
        new_directory_name = 'results/c3s/2_c3s_unique_by_automorphisms/' + str(i) + '_connecting_edges'

        graphs = gio.read_graph_files(directory_name)
        unique_graphs = gu.filter_isomorphisms_with_cycle_to_cycle_mapping(graphs)

        gio.save_graphs_in_directory(unique_graphs, new_directory_name)


# For two given graphs from the last iteration step, this function puts together all possible graphs with k C5s and saves those graphs, that are (P6, triangle)-free.
def find_possible_connections_c5s(method_input):
    (graph_1, graph_2, connections_2_c5s, k) = method_input
    for connecting_edges_3, possible_connections_2c5s in connections_2_c5s.items():
        if int(graph_1.edge_numbers[0]) <= int(connecting_edges_3):
            for graph_3 in possible_connections_2c5s:
                edge_numbers = graph_1.edge_numbers.copy()
                if len(graph_2.edge_numbers) <= 1:
                    edge_numbers.extend(graph_2.edge_numbers)
                else:
                    edge_numbers.extend(graph_2.edge_numbers[((k-2)*(k-3)) // 2:])
                edge_numbers.append(graph_3.edge_numbers[0])

                combined_graph = gu.combine_graph_from_last_iteration(graph_1, graph_2, graph_3, 5)
                if combined_graph.is_p6_triangle_free():
                    gio.save_graph(combined_graph, 5)


# For two given graphs from the last iteration step, this function puts together all possible graphs with k triangles and saves those graphs, that are (P6, K4, diamond)-free.
def find_possible_connections_c3s(method_input):
    (graph_1, graph_2, connections_2_c3s, k) = method_input
    for connecting_edges_3, possible_connections_2c3s in connections_2_c3s.items():
        if int(graph_1.edge_numbers[0]) <= int(connecting_edges_3):
            for graph_3 in possible_connections_2c3s:
                edge_numbers = graph_1.edge_numbers.copy()
                if len(graph_2.edge_numbers) <= 1:
                    edge_numbers.extend(graph_2.edge_numbers)
                else:
                    edge_numbers.extend(graph_2.edge_numbers[((k-2)*(k-3)) // 2:])
                edge_numbers.append(graph_3.edge_numbers[0])

                combined_graph = gu.combine_graph_from_last_iteration(graph_1, graph_2, graph_3, 3)
                if combined_graph.is_p6_diamond_k4_free():
                    gio.save_graph(combined_graph, 3)


# Collects all inputs for iteration step k of the 'find_possible_connections' method, that need to be checked. Therefore, for every graph with k-1 C5s from the last iteration step, we take another graph with k-1 C5s, that represents the connections between the first k-2 C5s and the new C5 that will be added. These pairs of graphs, together with a list of all possible connections between two C5s, are then used as inputs for running the 'find_possible_connections' method.
def start_execution(k, nodes_per_cycle):
    if nodes_per_cycle == 3:
        connections_2_cycles = gu.get_connections_2c3s()
        print(len(connections_2_cycles))
    elif nodes_per_cycle == 5:
        connections_2_cycles = gu.get_connections_2c5s()
    else:
        return

    connections_last_iteration = gu.get_connections_last_iteration(k, nodes_per_cycle)
    print(len(connections_last_iteration))
    unique_connections_last_iteration = gu.get_unique_connections_last_iteration(k, nodes_per_cycle)
    print(len(unique_connections_last_iteration))

    inputs = []
    for connecting_edges_1, possible_unique_connections_last_iteration_1 in unique_connections_last_iteration.items():
        for graph_1 in possible_unique_connections_last_iteration_1:
            for connecting_edges_2, possible_connections_last_iteration_2 in connections_last_iteration.items():
                for graph_2 in possible_connections_last_iteration_2:
                    if (k == 3 and int(graph_1.edge_numbers[0]) <= int(graph_2.edge_numbers[0])) or (k != 3 and graph_1.graph_numbers[:((k - 2) * (k - 3)) // 2] == graph_2.graph_numbers[:((k - 2) * (k - 3)) // 2]):
                        method_input = (graph_1, graph_2, connections_2_cycles, k)
                        inputs.append(method_input)

    print(len(inputs))

    if nodes_per_cycle == 3:
        gu.run_parallel(find_possible_connections_c3s, inputs)
    elif nodes_per_cycle == 5:
        gu.run_parallel(find_possible_connections_c5s, inputs)
    else:
        return


# Runs through the list of connections between k C5s. For each graph all proper precolorings of the first k-1 C5s are determined. For each precoloring it is checked, if it does not decompose the graph, then it is saved in the graph instance. Each graph that hasss at least one precoloring that does not decompose the graph, is saved in the results folder.
def find_possible_precolored_graphs(k, nodes_per_cycle):
    subfolders = gio.get_subfolders_with_suffix('results/c' + str(nodes_per_cycle) + 's/' + str(k) + '_c' + str(nodes_per_cycle) + 's', '_connecting_edges')
    for (subfolder, connecting_edges) in subfolders:
        graph_list = gio.read_graph_files(subfolder)

        for graph in graph_list:
            coloring_list = []
            if nodes_per_cycle == 3:
                if k == 3:
                    coloring_list = gc.generate_colorings_two_c3s()
                else:
                    for precoloring in graph.possible_precolorings:
                        coloring_list.extend(gc.generate_colorings_with_added_c3(precoloring))

            if nodes_per_cycle == 5:
                if k == 3:
                    coloring_list = gc.generate_colorings_two_c5s()
                else:
                    for precoloring in graph.possible_precolorings:
                        coloring_list.extend(gc.generate_colorings_with_added_c5(precoloring))

            graph.possible_precolorings = []

            for precoloring in coloring_list:
                (is_decomposed, coloring) = graph.decomposed_by_precoloring(precoloring, nodes_per_cycle)
                if not is_decomposed:
                    graph.possible_precolorings.append(precoloring.copy())

            if len(graph.possible_precolorings) > 0:
                cycle_number = len(graph.nodes()) // nodes_per_cycle
                edges = str(graph.edge_numbers[0])
                for edge_number in graph.edge_numbers[1:]:
                    edges += '_' + str(edge_number)
                path_name = 'results/c' + str(nodes_per_cycle) + 's/' + str(cycle_number) + '_c' + str(nodes_per_cycle) + 's_with_precoloring/' + str(
                    edges) + '_connecting_edges/' + graph.name + '.pkl'
                graph.save_to_pickle(path_name)


# Runs through the list of connections between k C5s that are equipped with a precoloring. Only saves one representative for each set of graphs, in which every graph is isomorphic to each other with an isomorphism that sends each C5 onto itself.
def find_possible_precolored_graphs_unique_by_automorphisms(k, nodes_per_cycle):
    subfolders = gio.get_subfolders_with_suffix('results/c' + str(nodes_per_cycle) + 's/' + str(k) + '_c' + str(nodes_per_cycle) + 's_with_precoloring', '_connecting_edges')
    for (subfolder, connecting_edges) in subfolders:
        graph_list = gio.read_graph_files(subfolder)

        unique_graphs = gu.filter_isomorphisms_with_cycle_to_cycle_mapping(graph_list)
        if len(unique_graphs) > 0:
            graph = unique_graphs[0]

            cycle_number = len(graph.nodes()) // nodes_per_cycle
            edges = str(graph.edge_numbers[0])
            for edge_number in graph.edge_numbers[1:]:
                edges += '_' + str(edge_number)
            path_name = 'results/c' + str(nodes_per_cycle) + 's/' + str(cycle_number) + '_c' + str(nodes_per_cycle) + 's_with_precoloring_unique_by_automorphisms/' + str(
                edges) + '_connecting_edges'
            path_name_plots = path_name + '_plots'

            gio.save_graphs_in_directory(unique_graphs, path_name)


# Returns a list of all graphs that consist of 3 C5s, where precoloring the first 2 C5s while applying the coloring restriction
def get_c5_graphs_where_color_3_appears_once_in_v():
    subfolders = gio.get_subfolders_with_suffix('results/c5s/3_c5s_with_precoloring_unique_by_automorphisms', '_connecting_edges')

    problematic_graphs = []
    for (subfolder, connecting_edges) in subfolders:
        graphs = gio.read_graph_files(subfolder)
        for graph in graphs:
            for coloring in graph.possible_precolorings:
                counter = 0
                for node in graph.nodes():
                    if node[0] == 'v' and coloring[node] == 3:
                        counter += 1
                if counter != 1:
                    problematic_graphs.append(graph)

    return problematic_graphs


def get_c5_graphs_with_multiple_precolorings(k):
    result_graphs = []
    subfolders = gio.get_subfolders_with_suffix('results/c5s/' + str(k) + '_c5s_with_precoloring_unique_by_automorphisms', '_connecting_edges')
    for (subfolder, connecting_edges) in subfolders:
        graphs = gio.read_graph_files(subfolder)
        for graph in graphs:
            if len(graph.possible_precolorings) > 1:
                result_graphs.append(graph)
    return result_graphs


# Groups all graph representatives that consist of 4 C5s into groups 1, 2, 3, depending on how many edges connect the green vertex in G3 to G1. The same happens for the connections of the green vertex to G2.
def group_c5_graphs_by_connections_last_green_node():
    subfolders = gio.get_subfolders_with_suffix('results/c5s/4_c5s_with_precoloring_unique_by_automorphisms', '_connecting_edges')

    groups_connections_to_u = {0: [], 1: [], 2: []}
    groups_connections_to_v = {0: [], 1: [], 2: []}

    for (subfolder, connecting_edges) in subfolders:
        graphs = gio.read_graph_files(subfolder)
        for graph in graphs:
            nodes_by_initial = graph.get_nodes_by_initial()
            green_nodes_in_w = [node for node in nodes_by_initial['w'] if graph.possible_precolorings[0][node] == 3]

            #We know, that there is eactly one node with color 3
            green_node_in_w = green_nodes_in_w[0]

            num_connections_to_u = len([node for node in nodes_by_initial['u'] if graph.has_edge(node, green_node_in_w)])
            num_connections_to_v = len([node for node in nodes_by_initial['v'] if graph.has_edge(node, green_node_in_w)])

            groups_connections_to_u[num_connections_to_u].append(graph)
            groups_connections_to_v[num_connections_to_v].append(graph)

    return groups_connections_to_u, groups_connections_to_v


if __name__ == "__main__":
    # graphs consisting of disjoint triangles
    # find_connections_2_c3s()
    # find_connections_2_c3s_with_filtered_automorphisms()
    # start_execution(3, 3)
    # find_possible_precolored_graphs(3, 3)
    # find_possible_precolored_graphs_unique_by_automorphisms(3, 3)
    # start_execution(4, 3)
    # find_possible_precolored_graphs(4, 3)
    # find_possible_precolored_graphs_unique_by_automorphisms(4, 3)
    # start_execution(5, 3)
    # find_possible_precolored_graphs(5, 3)
    # find_possible_precolored_graphs_unique_by_automorphisms(5, 3)
    # start_execution(6, 3)
    # find_possible_precolored_graphs(6, 3)
    # find_possible_precolored_graphs_unique_by_automorphisms(6, 3)
    # start_execution(7, 3)
    # find_possible_precolored_graphs(7, 3)
    # find_possible_precolored_graphs_unique_by_automorphisms(7, 3)
    # start_execution(8, 3)
    #
    # # graphs consisting of disjoint C5s
    find_connections_2_c5s()
    find_connections_2_c5s_with_filtered_automorphisms()
    start_execution(3, 5)
    find_possible_precolored_graphs(3, 5)
    find_possible_precolored_graphs_unique_by_automorphisms(3, 5)
    # start_execution(4, 5)
    # find_possible_precolored_graphs(4, 5)
    # find_possible_precolored_graphs_unique_by_automorphisms(4, 5)
    #
    # print('Number of graphs with 3 C5s, for which we can find a proper precoloring of G1 and G2, where color 3 appears twice in V(G1): ' + str(len(get_c5_graphs_where_color_3_appears_once_in_v())))
    #
    # print("Number of graphs with 4 c5s, for which there are more than one precoloring that doesn't decompose G4: " + str(len(get_c5_graphs_with_multiple_precolorings(4))))
    #
    # groups_connections_to_u, groups_connections_to_v = group_c5_graphs_by_connections_last_green_node()
    # print('Number of graphs with a green vertex with 2 edges to G1: ' + str(len(groups_connections_to_u[2])))
    # print('Number of graphs with a green vertex with 2 edges to G2: ' + str(len(groups_connections_to_v[2])))
