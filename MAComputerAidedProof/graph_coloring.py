import copy
import networkx as nx
import itertools


# Applies a precoloring to the color_lists of the given graph. If the resulting color list of at least one node is empty, the returned updated color_lists dictionary is empty.
def precolor(graph, color_lists, precoloring):
    cur_color_lists = copy.deepcopy(color_lists)
    for node, color in precoloring.items():
        cur_color_lists = update_color_lists(graph, cur_color_lists, node, color)
        if not cur_color_lists:
            break

    return cur_color_lists


# Sets the color list of the given node to only the given color and removes this color from the color lists of all neighboring nodes. If the color of a neighboring node is uniquely determined after that, the color lists are again updated, depending on that neighbor.
def update_color_lists(graph, color_lists, node, color):
    cur_color_lists = copy.deepcopy(color_lists)

    if color in cur_color_lists[node]:
        cur_color_lists[node] = [color]
    else:
        return {}

    for neighbor in nx.neighbors(graph, node):
        if color in cur_color_lists[neighbor]:
            cur_color_lists[neighbor].remove(color)

            if len(cur_color_lists[neighbor]) == 0:
                return {}
            elif len(cur_color_lists[neighbor]) == 1:
                cur_color_lists = update_color_lists(graph, cur_color_lists, neighbor, cur_color_lists[neighbor][0])
                if not cur_color_lists:
                    break

    return cur_color_lists


# Returns a coloring as a dictionary, given the color lists of a graph. If none of the color lists contain exactly one element, the returned coloring is empty.
def get_coloring_from_color_lists(color_lists):
    coloring = {}
    for node in color_lists:
        if len(color_lists[node]) == 1:
            coloring[node] = color_lists[node][0]

    return coloring


# The given graph has to consist of k C5s, given in some order that is determined by the initial character of their node names. It is checked, whether any node in the k'th C5 has 2 neighbors in either the first k-1 C5s. If that is the case, the color 3 is removed from the color list of each such node. After that the precoloring is applied.
def precolor_with_color_restriction(graph, color_lists, precoloring):
    cur_color_lists = copy.deepcopy(color_lists)
    groups_by_initial = graph.get_nodes_by_initial()
    last_c_5_node_name = max([node[0] for node in graph.nodes()])

    for node in groups_by_initial[last_c_5_node_name]:
        for initial, c5_nodes in groups_by_initial.items():
            if initial == 'u' or initial == 'v':
                edge_count = sum(1 for neighbor in graph.neighbors(node) if neighbor in c5_nodes)
                if edge_count >= 2:
                    cur_color_lists[node].remove(3)
                    break

    propagated_color_lists = precolor(graph, cur_color_lists, precoloring)
    return propagated_color_lists


# Generates all colorings of a C5 with the given nodes, that are rotations of the coloring {'u_0': 1, 'u_1': 2, 'u_2': 1, 'u_3': 2, 'u_4': 3}, so color 3 appears only once. Every proper coloring of a C5 can be received from these by permuting the colors.
def generate_colorings_c5(nodes):
    colorings = []
    for rotation in generate_rotations([1, 2, 1, 2, 3]):
        coloring = dict(zip(nodes, rotation))
        colorings.append(coloring)
    return colorings


# Generates all colorings of a triangle with the given nodes, that are rotations of the coloring {'u_0': 1, 'u_1': 2, 'u_2': 3}. Every proper coloring of a triangle can be received from these by permuting the colors.
def generate_colorings_c3(nodes):
    colorings = []
    for rotation in generate_rotations([1, 2, 3]):
        coloring = dict(zip(nodes, rotation))
        colorings.append(coloring)
    return colorings


# Generates all rotations of a list
def generate_rotations(lst):
    rotations = []
    for i in range(len(lst)):
        rotations.append(lst[i:] + lst[:i])
    return rotations


# Generates all colorings that result from permuting the colors in the given coloring
def permute_coloring(coloring):
    nodes = list(coloring.keys())
    colors = list(coloring.values())
    color_set = set(colors)
    permutations = itertools.permutations(color_set)

    permuted_colorings = []
    for perm in permutations:
        perm_coloring = {nodes[i]: perm[(colors[i] - 1) % 3] for i in range(len(nodes))}
        permuted_colorings.append(perm_coloring)

    return permuted_colorings


# Generates all colorings of two C5s, not regarding the edges running between the C5s, where the colorings of the first C5 are rotations of the coloring {'u_0': 1, 'u_1': 2, 'u_2': 1, 'u_3': 2, 'u_4': 3}, so color 3 appears only once. Every coloring of two C5s can be received from these by permuting the colors. The returned colorings are not necessarily proper.
def generate_colorings_two_c5s():
    colorings_u = generate_colorings_c5(['u0', 'u1', 'u2', 'u3', 'u4'])

    colorings_v_wo_permutation = generate_colorings_c5(['v0', 'v1', 'v2', 'v3', 'v4'])
    colorings_v_set = []

    for coloring in colorings_v_wo_permutation:
        colorings_v_set.extend(permute_coloring(coloring))

    colorings_v = list(colorings_v_set)

    colorings_u_v = []
    for coloring_u in colorings_u:
        for coloring_v in colorings_v:
            colorings_u_v.append(coloring_u | coloring_v)
    return colorings_u_v


# Generates all colorings of two triangles, not regarding the edges running between the triangles, where the colorings of the first triangle are rotations of the coloring {'u_0': 1, 'u_1': 2, 'u_2': 3}. Every coloring of a two triangles can be received from these by permuting the colors. The returned colorings are not necessarily proper.
def generate_colorings_two_c3s():
    colorings_u = generate_colorings_c3(['u0', 'u1', 'u2'])

    colorings_v_wo_permutation = generate_colorings_c3(['v0', 'v1', 'v2'])
    colorings_v_set = []

    for coloring in colorings_v_wo_permutation:
        colorings_v_set.extend(permute_coloring(coloring))

    colorings_v = list(colorings_v_set)

    colorings_u_v = []
    for coloring_u in colorings_u:
        for coloring_v in colorings_v:
            colorings_u_v.append(coloring_u | coloring_v)
    return colorings_u_v


# coloring_wo_c5 has to be a coloring of a graph that consists of k-1 C5s. The method generates all colorings for a k'th C5 and returns all combinations of them with the input coloring. The returned coloring is not necessarily proper.
def generate_colorings_with_added_c5(coloring_wo_c5):
    latest_char = max([key[0] for key in coloring_wo_c5.keys()])
    node_char = chr(ord(latest_char) + 1)

    node_names = [str(node_char) + str(i) for i in range(5)]

    colorings_wo_permutation = generate_colorings_c5(node_names)
    colorings_list = []

    for coloring in colorings_wo_permutation:
        colorings_list.extend(permute_coloring(coloring))

    resulting_colorings = []
    for coloring_new_c5 in colorings_list:
        resulting_colorings.append(coloring_wo_c5 | coloring_new_c5)
    return resulting_colorings


# coloring_wo_c3 has to be a coloring of a graph that consists of k-1 triangles. The method generates all colorings for a k'th triangle and returns all combinations of them with the input coloring. The returned coloring is not necessarily proper.
def generate_colorings_with_added_c3(coloring_wo_c3):
    latest_char = max([key[0] for key in coloring_wo_c3.keys()])
    node_char = chr(ord(latest_char) + 1)

    node_names = [str(node_char) + str(i) for i in range(3)]

    colorings_wo_permutation = generate_colorings_c3(node_names)
    colorings_list = []

    for coloring in colorings_wo_permutation:
        colorings_list.extend(permute_coloring(coloring))

    resulting_colorings = []
    for coloring_new_c3 in colorings_list:
        resulting_colorings.append(coloring_wo_c3 | coloring_new_c3)
    return resulting_colorings
