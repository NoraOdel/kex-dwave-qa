# testing : https://www.youtube.com/watch?v=jTDnGox0c9Y

# QUESTIONS?
# Which solver should we run this on?
from dwave.system import DWaveSampler, EmbeddingComposite # = embedding is done by Dwave
from dimod import BinaryQuadraticModel
from collections import defaultdict


# Constants
num_reads = 5
big_penalty = 5
semi_big_penalty = 2
zero_penalty = 0



# Set upp scenario
# Assertions: 
#       1.
#       2. edges has to be a adjecency graph where value is 1 if the relevant nodes have an edge between them else 0

nodes = [0,1]
edges = [[0,1],
        [1,0]] 
n = len(nodes)

# Initialize our h vector, J matrix
def default_value():
    return 0

h = defaultdict(default_value)
J = defaultdict(default_value)


# Build variables for each pair of vertices
pairs = [(nodes[xi], nodes[yi]) for xi in range(n-1) for yi in range(xi+1, n)]
n_pairs = len(pairs)
assert n_pairs == (n^2-n)/2, "Number of distinct pairs should be (n^2-n)/2 but its not."

print("hej")
for p1i in range(n_pairs):
    p1 = pairs[p1i]
    i, j = p1[0], p1[1]
    if edges[i][j] == 1:                        # Penalty when they share the same color, promotes x_ij = -1
        h[f'Bias {p1}'] = big_penalty           # big bias
    else:                                       # No penalty, but promotes x_ij = 1 since we want to minimize #sets
        h[f'Bias {p1}'] = -semi_big_penalty     # Negative since we promote the behaviour, ... 
                                                # ... Semi-big bias since Quadratic Coefficience should matter more... TODO: why?

    print(i)
    for p2i in range(p1i+1, n_pairs):
        p2 = pairs[p2i]
        k, h = p2[-1], p2[-2] 

        if i == k:
            exclusively_p1_node, exclusively_p2_node, p1_and_p2_node = j, h, i
        elif j == k:
            exclusively_p1_node, exclusively_p2_node, p1_and_p2_node = i, h, j
        elif i == h:
            exclusively_p1_node, exclusively_p2_node, p1_and_p2_node = j, k, i
        elif j == h:
            exclusively_p1_node, exclusively_p2_node, p1_and_p2_node = i, k, j
        else:
            J[f'Weight {(p1, p2)}'] = zero_penalty   # No penalty or promotion if they do not have anything todo with eachother
            continue
        
        if edges[exclusively_p1_node][exclusively_p2_node] == 1:    # Penalty if they break the condition, and if x_ij = x_hk -1 (TODO: we do not want this last part)
            J[f'Weight {(p1, p2)}'] = big_penalty                   # Promotes x_ij = -1 and p_hk = 1 or vice versa
        else:
            J[f'Weight {(p1, p2)}'] = -semi_big_penalty     # Promotes x_ij = 1 and p_hk = 1 and x_ij = -1 and p_hk = -1 (TODO: we do not want this last part)
                                                            # TODO: should promote Promotes x_ij = -1 and p_hk = 1 or vice versa more than x_ij = -1 and p_hk = -1 

        
        

            




        


    
 


# Initialize BQM
#bqm = BinaryQuadraticModel('BINARY')

# Create Objective
