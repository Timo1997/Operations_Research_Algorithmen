import numpy as np
import pandas as pd


def dijkstra_algorithm(Graph, start_node):
    is_continuing = True

    # informations for output
    # Node 1, new_distance < old_distance, No/Yes new_distance(finder_node) 
    info_new_distances = []
    dfs_new_distances = []

    # distance from start_node to node (sum of edge weights)
    node_to_distance = {}

    # checks if node is already a selected node
    node_to_is_finished = {}

    # saves all the solution information about the dijkstra algorithm
    # {selected_node: {node: new_distance0, node: new_distance1,..},...}
    node_to_node_to_distance = {0: {start_node: 0}}
    
    # prefill the dicitonaries
    for node in Graph.nodes():
        node_to_distance[node] = np.inf
        node_to_is_finished[node] = False
        
    #begin at start_node
    node_to_distance[start_node] = 0



    while is_continuing == True:
        # check if there are not selected but already found nodes
        is_continuing = node_available_dijkstra(Graph, node_to_distance, node_to_is_finished)
        if is_continuing == False:
            break

        # select unselected node with the smallest distance
        selected_node = selected_node_dijkstra(Graph,node_to_distance ,node_to_is_finished)
        node_to_is_finished[selected_node] = True

        # save all the nodes with the new distance which get inproved in this iteration
        node_to_new_distance = {}  # {node: new_distance, node: new_distance,...}
        info_new_distances = []

        # check all outgoing edges from selected_node
        for start_edge, end_edge, weight in Graph.edges(selected_node, data="weight"):
            # check if new distance is better than old distance
            if node_to_distance[end_edge] > node_to_distance[selected_node] + weight:
                # save data of new distance
                info_new_distances.append(["Node " + str(end_edge), str(node_to_distance[selected_node]) + "+" +
                                           str(weight) + "=" + str(node_to_distance[selected_node] + weight) + 
                                           "<" + str(node_to_distance[end_edge]), "Yes - " + 
                                           str(node_to_distance[selected_node] + weight) + "(" + str(selected_node) + ")"])
                node_to_distance[end_edge] = node_to_distance[selected_node] + weight
                node_to_new_distance[end_edge] = node_to_distance[end_edge]
            elif node_to_is_finished[end_edge] == False:
                # when node is not selected and old distance is better than new_distance, also save that data 
                info_new_distances.append(["Node " + str(end_edge), str(node_to_distance[selected_node]) + "+" +
                                           str(weight) + "=" + str(node_to_distance[selected_node] + weight) + 
                                           "<" + str(node_to_distance[end_edge]), "No"])

        # choosing selected_node, save nodes with improved distances           
        node_to_node_to_distance[selected_node] = node_to_new_distance

        dfs_new_distances.append(pd.DataFrame(info_new_distances, 
                                              columns=["Adjacent Node", "Distance from Assigned Node",
                                                      "New Temporary Label at Adjacent Node?"]))

    return node_to_node_to_distance, dfs_new_distances


def node_available_dijkstra(Graph, node_to_distance, node_to_is_finished):
    # search for possible nodes that are already found and not yet selected
    for node in Graph.nodes():
        if node_to_distance[node] < np.inf and node_to_is_finished[node] == False:
            return True
    return False


def selected_node_dijkstra(Graph,node_to_distance , node_to_is_finished):
    min_value = np.inf
    selected_node = 0

    # search the not selected node with the smallest length/distance
    for node in Graph.nodes():
        if node_to_is_finished[node] == False and node_to_distance[node] < min_value:
            min_value = node_to_distance[node]
            selected_node = node
    return selected_node




