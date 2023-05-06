# TODO: Which solver should we run this on?
from dwave.system import DWaveSampler, EmbeddingComposite # = embedding is done by Dwave
import dwave.inspector
from dimod import BinaryQuadraticModel
from QUBO_helper import build_QUBO_matrix
import numpy as np
import time 
import datetime as dt


# CQM
from dimod import DiscreteQuadraticModel, Binary
from dwave.system import LeapHybridDQMSampler

# Constants
NUM_READS = 1000                 # Hyperparameter TODO: Increase? 1000?
CHAIN_STRENGTH = 400              # Hyperparameter TODO: to be greater than biases

def solveGCP(nodes: [int], edges: [[int]], realChromaticNumber: int):
    """
    Return the approxminated chromatic number of a graph \\
    using Quantum Annealing with a binary quadratic model
    """
    n = len(nodes)

    # Pre-Processing
    tic = time.perf_counter()
    Q = build_QUBO_matrix(n, nodes, edges)
    toc = time.perf_counter()
    pre_processing_time = toc - tic
    

    # Embedding + Quantum Annaeling 
    sampler = EmbeddingComposite(DWaveSampler(solver={'topology__type': 'pegasus'}))

    tic = time.perf_counter()
    results = sampler.sample_qubo(Q,
                                    num_reads=NUM_READS,
                                    chain_strength=CHAIN_STRENGTH,
                                    label='KEX - Graph Coloring - BQM')
    toc = time.perf_counter()
    QA_time = toc - tic


    best_solution = results.first.sample

    # Post processing, calculate number of colors from resulting graph coloring
    tic = time.perf_counter()
    chromatic = getChromaticNumber(best_solution, n)
    toc = time.perf_counter()
    post_processing_time = toc - tic
 
    # collect results
    collected = collectResults(results, 
                                best_solution, 
                                realChromaticNumber,
                                chromatic, 
                                QA_time,
                                pre_processing_time, 
                                post_processing_time)

    # Print approximated chromatic number
    return collected


def solveGCPcqm(nodes: [int], edges: [[int]], realChromaticNumber: int):
    tic = time.perf_counter()
    num_colors = len(nodes)
    colors = range(num_colors)

    dqm = DiscreteQuadraticModel()

    for node in nodes:
        dqm.add_variable(num_colors, label=node)
        dqm.set_linear(node, colors)


    # Build dqm variables
    for i1 in range(len(nodes)):
        node1 = nodes[i1]
        for i2 in range(i1+1,len(nodes)):
            node2 = nodes[i2]
            if edges[node1][node2] == 1: # Penalty
                dqm.set_quadratic(node1, node2, {(color, color): 100 for color in colors})
    toc = time.perf_counter()
    pre_processing_time = toc - tic

    tic = time.perf_counter()
    results = LeapHybridDQMSampler().sample_dqm(dqm, label='DQM - Graph Coloring')
    toc = time.perf_counter()
    QA_time = toc - tic

    best_solution = results.first.sample
    # Get chromatic number - Post processing
    tic = time.perf_counter()
    usedColors = dict.fromkeys(colors, 0)
    for color in best_solution.values():
        usedColors[color] = 1
    
    chromatic = sum(usedColors.values())
    toc = time.perf_counter()
    post_processing_time = toc - tic
            
    # collect results
    collected = collectResultsDQM(results, 
                                best_solution, 
                                realChromaticNumber,
                                chromatic, 
                                QA_time,
                                pre_processing_time, 
                                post_processing_time)


    print(collected)

def collectResultsDQM(results, 
                    best_solution, 
                    realChromaticNumber,
                    chromatic, 
                    QA_time,
                    pre_processing_time, 
                    post_processing_time):
    # PREFORMANCE
    qpu_access_time = results.info['qpu_access_time'] # microseconds


    collected = {
        # Accuracy
        'RealChromaticNumber': realChromaticNumber,
        'CalculatedChromaticNumber': chromatic, 

        # Performances
        'QPUAccessTime': qpu_access_time / 1000, 
        'TotalServiceTime': QA_time * 1000, 
        'PreProcessing': pre_processing_time * 1000, 
        'PostProcessing': post_processing_time * 1000,
    }

    return collected

    

def collectResults(results, best_solution, realChromaticNumber, chromatic, QA_time, pre_processing_time, post_processing_time):

    # PREFORMANCE
    qpu_access_time = results.info['timing']['qpu_access_time'] # microseconds

    # Other
    chain_strength =  results.info['embedding_context']['chain_strength']


    collected = {
        # Accuracy
        'RealChromaticNumber': realChromaticNumber,
        'CalculatedChromaticNumber': chromatic, 

        # Performances
        'QPUAccessTime': qpu_access_time / 1000, 
        'TotalServiceTime': QA_time * 1000, 
        'PreProcessing': pre_processing_time * 1000, 
        'PostProcessing': post_processing_time * 1000,

        # Other
        'ChainStrength': chain_strength 
    }

    return collected



def getChromaticNumber(solution, n):
    grouped = np.zeros(n)
    newGroupId = 1

    chromatic = n
    for key in solution.keys():
        (x, y) = key
        if (solution[key] == 1):
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
    return chromatic
