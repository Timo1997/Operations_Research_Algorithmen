import networkx as nx
import pandas as pd

def prim_algorithm(Graph, start_node):
    #Format [start_node_edge, end_node_edge, weight, is_next_selected_node ]
    possible_edges = []
    path_edges = []
    
    path_nodes = [start_node]
    dfs_possible_edges = []
    
    start_edge_id = 0
    end_edge_id = 1
    weight_id = 2
    is_selected_id = 3
    
    while len(path_nodes) != Graph.number_of_nodes():
        #get all possible selectable edges
        possible_edges = get_all_possible_edges(Graph, path_nodes)

        #select edge with smallest edge_weight
        selected_edge = min(possible_edges, key=lambda x: x[weight_id]) 
        selected_edge[is_selected_id] = True
        
        #create df for current iteration
        possible_edges = sorted(possible_edges, key=lambda x: (x[start_edge_id], x[end_edge_id]))
        dfs_possible_edges.append(pd.DataFrame(possible_edges, columns = ["Startnode", "Endnode", "Edgevalue", "Selected"]))
        
        #Update lists 
        path_nodes.append(selected_edge[end_edge_id])
        path_edges.append(selected_edge)
        
    return path_edges, path_nodes, dfs_possible_edges


def get_all_possible_edges(Graph, path_nodes):
    #get all outgoing edges of nodes in path_edges 
    #format (start_node_edge, end_node_edge, weight)
    possible_edges = list(Graph.edges(path_nodes, data = "weight"))
    #change tuples to list format
    possible_edges = [list(edge) for edge in possible_edges]
    
    #delete edges that show to nodes that are in path_nodes
    #add "False" to every edge
    end_edge_id = 1
    for edge in reversed(possible_edges):
        edge.append(False)    
        if edge[end_edge_id] in path_nodes:
            possible_edges.remove(edge)
    return possible_edges

