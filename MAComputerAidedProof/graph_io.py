import os
import custom_graph


# Helper function to save a graph in the correct folder depending on its properties
def save_graph(graph, with_plot=False):
    c_5_number = len(graph.nodes()) // 5
    edges = str(graph.edge_numbers[0])
    for edge_number in graph.edge_numbers[1:]:
        edges += '_' + str(edge_number)

    path_name = 'results/c5s/' + str(c_5_number) + '_c5s/' + str(edges) + '_connecting_edges/' + graph.name + '.pkl'
    graph.save_to_pickle(path_name)

    if with_plot:
        path_name_plot = 'results/c5s/' + str(c_5_number) + '_c5s/' + str(edges) + '_connecting_edges_plots/' + graph.name + '.png'
        graph.draw_and_save(path_name_plot, graph.possible_precolorings[0])


# Saves a list of graphs
def save_graphs_in_directory(graph_list, directory_name):
    for graph in graph_list:
        file_path = directory_name + '/' + graph.name + '.pkl'
        graph.save_to_pickle(file_path)


# Saves the plots of a list of graphs
def save_graph_plots_in_directory(graph_list, directory_name):
    for graph in graph_list:
        file_path = directory_name + '/' + graph.name + '.png'
        if not graph.possible_precolorings:
            graph.draw_and_save(file_path, {})
        else:
            graph.draw_and_save(file_path, graph.possible_precolorings[0])


# Reads all graph files found in a directory
def read_graph_files(directory_name):
    files = os.listdir(directory_name)

    graph_files = [f for f in files if f.endswith('.pkl')]

    graphs = []

    for graph_file in graph_files:
        graph_path = os.path.join(directory_name, graph_file)
        graph = custom_graph.CustomGraph.load_from_pickle(graph_path)
        graphs.append(graph)

    return graphs


# Finds all subfolders with a given suffix
def get_subfolders_with_suffix(directory, suffix):
    result = []
    for root, dirs, files in os.walk(directory):
        for subfolder in dirs:
            if subfolder.endswith(suffix):
                extracted = subfolder[:-len(suffix)]
                result.append((directory + '/' + str(subfolder), extracted))
        break
    return result
