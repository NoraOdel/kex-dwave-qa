from collections import defaultdict


BIG_PENALTY = 300
SMALL_PROMOTION = 5           # Hyperparameter TODO
ZERO_PENALTY = 0                # Hyperparameter TODO

# Initialize our matrix Q, for Q in build_QUBO_matrix()
def default_value():
    return 0

# Building Q= 
# ....
def build_QUBO_matrix(n_nodes, nodes, edges):
    """
    Translates the graph coloring problem to a QUBO and returns the corresponding QUBO matrix 
    """

    # QUBO
    Q = defaultdict(default_value)

    # Build variables for each pair of vertices
    pairs = [(nodes[xi], nodes[yi]) for xi in range(n_nodes-1) for yi in range(xi+1, n_nodes)]
    n_pairs=len(pairs)
    assert n_pairs == (n_nodes**2-n_nodes)/2, "Number of distinct pairs should be (n^2-n)/2 but its not."

    for pair1_index in range(n_pairs):
        pair1 = pairs[pair1_index]
        node1, node2 = pair1[0], pair1[1]
        if edges[node1][node2] == 1:   
            Q[(pair1,pair1)] = BIG_PENALTY                  # big penalty: should outshadow promotion of pair1 = 1 in quadratic coefficients 
                                                            # -> Happens when two pairs could in respect to eachother be in the same grouping    
            # promotes x_ij = 0
                                                
        else:
            Q[(pair1,pair1)] = -SMALL_PROMOTION            # semi-big penalty/promotion: should not outshadow promotion of  pair1 = 0 in quadratic coefficients
                                                            # -> happens when two pairs, in respect to eachother, can not be in the same grouping    
            # promotes x_ij = 1

        for pair2_index in range(pair1_index+1, n_pairs):
            pair2 = pairs[pair2_index]
            node3, node4 = pair2[0], pair2[1] 

            if node1 == node3:
                exclusively_p1_node, exclusively_p2_node = node2, node4
            elif node2 == node3:
                exclusively_p1_node, exclusively_p2_node = node1, node4
            elif node1 == node4:
                exclusively_p1_node, exclusively_p2_node = node2, node3
            elif node2 == node4:
                exclusively_p1_node, exclusively_p2_node = node1, node3
            else:
                Q[(pair1,pair2)] = ZERO_PENALTY                               # No penalty or promotion if they do not have anything todo with eachother
                continue
            
            pair3 = (exclusively_p1_node, exclusively_p2_node)
            
            if edges[exclusively_p1_node][exclusively_p2_node] == 1:
                Q[(pair1,pair2)] = BIG_PENALTY                                # Big penalty, should outshadow promotion of 1 in linear coefficients
                # Promotes  x_node1,node2 = 0 and p_node3,node4 = 1 or 
                #           x_node1,node2 = 1 and p_node3,node4 = 0 or
                #    case3: x_node1,node2 = 0 and p_node3,node4 = 0 
                # case3 is not preferable, but acceptable due to promotions through linear coefficients
                # reason: we cannot promote case1 and case 2 if we do not check if the pairs should be able to 
                # have an edge between themselves. this is done with linear coefficients
            else:
                Q[(pair1,pair2)] = -SMALL_PROMOTION                # Semi-big penalty/promotion: should not outshadow promotion of 0 in linear coefficients
                                                                    # -> promotion happens when there is an edge between nodes in pair1/pair2
                # Promotes x_ij = 1 and p_hk = 1, everything else is equally good.
                # reason: we cannot promote case1 and case2 if we do not check if the pairs should be able to 
                # have an edge between themselves. this is done with linear coefficients
            

            if edges[node1][node2] == 1:
                Q[(pair2,pair3)] = BIG_PENALTY 
            
            

    return Q
