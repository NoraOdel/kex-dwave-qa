# TODO: Which solver should we run this on?
from dwave.system import DWaveSampler, EmbeddingComposite # = embedding is done by Dwave
import dwave.inspector
from dimod import BinaryQuadraticModel
from QUBO_helper import build_QUBO_matrix
import numpy as np

# Constants
NUM_READS = 100                 # Hyperparameter TODO: Increase? 1000?
CHAIN_STRENGTH = 20              # Hyperparameter TODO: to be greater than biases

def solveGCP(nodes: [int], edges: [[int]]):
    """
    Return the approxminated chromatic number of a graph \\
    using Quantum Annealing with a binary quadratic model
    """
    print(f'Chain Strength: {CHAIN_STRENGTH}')
    n = len(nodes)

    # CREATE QUBO Matrix
    Q = build_QUBO_matrix(n, nodes, edges)

    # Automatic Embedding in D-wave systems
    sampler = EmbeddingComposite(DWaveSampler())

    # sample_qubo -> Creates bqm from QUBO matrix and runs annealing process
    # returns sampled (approximated) solutions.
    sampleset = sampler.sample_qubo(Q,
                                    num_reads=NUM_READS,
                                    chain_strength=CHAIN_STRENGTH,
                                    label='KEX - Graph Coloring - BQM')


    # Post processing, calculate number of colors from resulting graph coloring
    print(sampleset)

    if len(nodes) == 8:
        dwave.inspector.show(sampleset)

    best_solution = sampleset.first.sample
    print(f'Best Solution according to QA: {best_solution}')
    try: 
        print(f'Chain Breaks: {best_solution.chain_breaks}')
    except:
        print("Not right command")


    grouped = np.zeros(n)
    newGroupId = 1

    chromatic = n
    for key in best_solution.keys():
        (x, y) = key
        if (best_solution[key] == 1):
            if grouped[y] == 0 and grouped[x] != 0:
                # x is grouped -> Group y with x
                chromatic -= 1
                grouped[y] = grouped[x]

            elif grouped[x] == 0 and grouped[y] != 0:
                # Group x
                chromatic -= 1
                grouped[x] = grouped[y]

            elif grouped[x] == 0 and grouped[y] == 0:
                # Group x and y in newGroup
                chromatic -= 1
                grouped[x] = newGroupId
                grouped[y] = newGroupId
                newGroupId += 1

            else: # grouped[x] != 0 and grouped[y] != 0
                # x and y are grouped, Should be grouped together.
                # If not grouped together -> Merge groups
                if grouped[y] != grouped[x]: 
                    # Remove one group
                    chromatic -= 1

                    # Merge Groups
                    for index in range(len(grouped)):
                        if grouped[index] == grouped[y]:
                            grouped[index] = grouped[x]
                        elif grouped[index] > grouped[y]:
                            grouped[index] -= 1
                    grouped[y] = grouped[x]
                    newGroupId -= 1
                # if grouped together -> do nothing
                            
    # Print approximated chromatic number
    return chromatic

