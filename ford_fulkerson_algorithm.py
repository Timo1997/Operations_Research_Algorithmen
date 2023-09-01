import networkx as nx
import pandas as pd


def ford_fulkerson_algorithm(Graph, start_node, end_node):    
    graphs = [Graph]
    graph_counter = 0
    info_iterations = [] #[iteration, path, restricting edge, flow]

    while True:
        #find path from  start node to end node
        #select one of the two following options!!!!
  
        #path_nodes, path_edges,is_path_available = find_path_by_node_number(graphs[graph_counter], start_node, end_node)
        path_nodes, path_edges, is_path_available = breadth_first_search(graphs[graph_counter], start_node , end_node)
  
        if is_path_available == False:
            break
            
        #make copy of graph to make changes on that copy
        graphs.append(graphs[graph_counter].copy())
        graph_counter += 1
        
        #find restricting edge and the flow value for this path
        weight_id = 2
        min_capacity_edge = min(path_edges,key=lambda x: x[weight_id])
        min_weight_of_path = min_capacity_edge[weight_id] 
        
        #make changes on Graph
        adjust_weight_of_edges(graphs[graph_counter], path_edges, min_weight_of_path)
        highlight_path_edges(graphs[graph_counter], path_edges)

        info_iterations.append([graph_counter, path_nodes,  min_capacity_edge[:-1], min_weight_of_path])
       
    
    df_ford_fulkerson = pd.DataFrame(info_iterations, columns = ["Iteration", "Augmenting Path", "restricting Edge", "Flow"])
    return graphs, df_ford_fulkerson



def adjust_weight_of_edges(Graph, path_edges, min_weight):
    start_node_id = 0
    end_node_id = 1
    #add path weight to original edges and substract from inverese edges
    for edge_nodes in path_edges:
        Graph[edge_nodes[start_node_id]][edge_nodes[end_node_id]]["weight"] -= min_weight
        Graph[edge_nodes[end_node_id]][edge_nodes[start_node_id]]["weight"] += min_weight
        
        
def highlight_path_edges(Graph, path_edges):
    copy_path_edges = path_edges.copy()
    start_node_id = 0
    end_node_id = 1
    
    #old path needs to be recolored to black
    for edge in Graph.edges():
        Graph[edge[start_node_id]][edge[end_node_id]]["color"]= "black"
        Graph[edge[end_node_id]][edge[start_node_id]]["color"]= "black"
    
    #current path should be orange    
    for path_edge in path_edges:
        Graph[path_edge[start_node_id]][path_edge[end_node_id]]["color"]= "orange"
        Graph[path_edge[end_node_id]][path_edge[start_node_id]]["color"]= "orange"
            
            
def breadth_first_search(Graph, start_node, end_node):
    found_nodes = [start_node]
    last_found_nodes  = [start_node]
    finder_edges = []
    is_edge_found = False
    
    end_edge_id = 1 
    weight_id = 2
    
    #as long as new nodes get discovered
    while len(last_found_nodes) > 0:
        new_found_nodes = []
        
        #look at every new possible edge
        for last_found_node in last_found_nodes:
            for outgoing_edge in Graph.edges(last_found_node, data = "weight"):
                
                #ignore edge when weight is 0
                if outgoing_edge[weight_id] == 0:
                    continue
                    
                #is a new node found?
                end_edge = outgoing_edge[end_edge_id]
                if end_edge not in found_nodes:
                    #save all data to the new found node
                    finder_edges.append(outgoing_edge)
                    found_nodes.append(end_edge)
                    new_found_nodes.append(end_edge)
                    
        #update list for next iteration
        last_found_nodes = new_found_nodes
    
    path_nodes, path_edges, is_path_available = construct_path(finder_edges, start_node, end_node)
    
    return path_nodes, path_edges, is_path_available
    
    
#reconstruct the path with the finder_edges 
def construct_path(finder_edges, start_node, end_node):
    path_nodes = [end_node]
    path_edges = []
    node = end_node
    while node != start_node:
        is_edge_found = False
        #look for edges that are connected to end_node
        for start_edge, end_edge, weight in finder_edges:
            if end_edge == node:
                node = start_edge
                path_edges.insert(0,[start_edge, end_edge, weight])
                path_nodes.insert(0, start_edge)
                is_edge_found = True

        #quit when start_node cant be found
        if is_edge_found == False:
            return None, None, False

    return path_nodes, path_edges, True   
    
    
def find_path_by_node_number(Graph, start_node, end_node):
    node = start_node #recently selected node
    path_nodes= [start_node]
    path_edges= []
    dead_end_edges = [] #edges that lead to nodes with 0 possible edges
    is_path_available = True
    
    start_edge_id = 0
    end_edge_id = 1
    weight_id = 2
    
    while node != end_node:
        #sort possible edges by node number
        edges_leaving_node = sorted(list(Graph.edges(node, data="weight")),key=lambda x: x[end_edge_id])
        
        #remove edges, which can't be used
        for edge in reversed(edges_leaving_node):
            #no capacity on edge
            if edge[weight_id] == 0:
                edges_leaving_node.remove(edge)
            #edge leads back to path (circle)
            elif edge[end_edge_id] in path_nodes:
                edges_leaving_node.remove(edge)
            
            #remove edges, which lead to a dead end
            for dead_end_edge in dead_end_edges:
                if edge[start_edge_id] == dead_end_edge[start_edge_id] and edge[end_edge_id] == dead_end_edge[end_edge_id] and edge in edges_leaving_node:
                    edges_leaving_node.remove(edge)
                
        #no path leads from start to finish_node
        if len(edges_leaving_node) == 0 and node == start_node:
            is_path_available = False
            return None,None, is_path_available
        #no path found so go back to previous node, last edge is a dead end
        elif len(edges_leaving_node) == 0 and node != start_node:
            dead_end_edges.append(path_edges.pop(-1))
            path_nodes.pop(-1)
            node = path_nodes[-1]
            continue    
        
        selected_edge = edges_leaving_node[0]
        node = selected_edge[end_edge_id] 
        path_edges.append([selected_edge[start_edge_id], selected_edge[end_edge_id], selected_edge[weight_id]])
        path_nodes.append(node)
        
    return path_nodes, path_edges, is_path_available
