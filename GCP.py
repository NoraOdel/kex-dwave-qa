from dwave.system import DWaveSampler, EmbeddingComposite, LeapHybridDQMSampler
from dimod import BinaryQuadraticModel, DiscreteQuadraticModel, Binary
from QUBO_helper import build_QUBO_matrix
import time 
import numpy as np

# Constants
NUM_READS = 100                   # Hyperparameter TODO: Increase? 1000?
CHAIN_STRENGTH = 400              # Hyperparameter TODO: to be greater than biases

def solveGCPbqm(nodes: [int], edges: [[int]], realChromaticNumber: int):
    """
    Return the approxminated chromatic number of a graph \\
    using Quantum Annealing with a binary quadratic model
    """
    # BUILD BQM
    tic = time.perf_counter()                       # TIMING

    n = len(nodes)
    Q = build_QUBO_matrix(n, nodes, edges)

    toc = time.perf_counter()                       # TIMING
    pre_processing_time = toc - tic                 # TIMING
    tic = time.perf_counter()                       # TIMING

    # RUN QUANTUM ANNEALING and FETCH SOLUTION
    sampler = EmbeddingComposite(DWaveSampler(solver={'topology__type': 'pegasus'}))
    results = sampler.sample_qubo(Q,
                                    num_reads=NUM_READS,
                                    chain_strength=CHAIN_STRENGTH,
                                    label='KEX - Graph Coloring - BQM')

    toc = time.perf_counter()                       # TIMING
    QA_time = toc - tic                             # TIMING
    tic = time.perf_counter()                       # TIMING

    # POST-PROCESSING - Get chromatic number from solution
    best_solution = results.first.sample
    chromatic = getChromaticNumberBQM(best_solution, n)
    
    toc = time.perf_counter()                       # TIMING
    post_processing_time = toc - tic                # TIMING
 
    # collect results
    solverChip = sampler.properties['child_properties']['chip_id']
    collected = collectResultsBQM(results, 
                                realChromaticNumber,
                                chromatic, 
                                QA_time,
                                pre_processing_time, 
                                post_processing_time,
                                solverChip)

    return collected

def solveGCPdqm(nodes: [int], edges: [[int]], realChromaticNumber: int):
    tic = time.perf_counter()                       # TIMING

    # BUILD DISCRETE QUADRATIC MODEL
    num_colors = len(nodes)
    colors = range(num_colors)

    dqm = DiscreteQuadraticModel()
    for node in nodes:
        dqm.add_variable(num_colors, label=node)
        dqm.set_linear(node, colors)

    for i1 in range(len(nodes)):
        node1 = nodes[i1]
        for i2 in range(i1+1,len(nodes)):
            node2 = nodes[i2]
            if edges[node1][node2] == 1: 
                dqm.set_quadratic(node1, node2, {(color, color): 100 for color in colors})
    
    toc = time.perf_counter()                       # TIMING
    pre_processing_time = toc - tic                 # TIMING
    tic = time.perf_counter()                       # TIMING

    # RUN QUANTUM ANNEALING and FETCH SOLUTION
    dqm_sampler = LeapHybridDQMSampler()
    results = dqm_sampler.sample_dqm(dqm, label='DQM - Graph Coloring')

    toc = time.perf_counter()                       # TIMING
    QA_time = toc - tic                             # TIMING
    tic = time.perf_counter()                       # TIMING


    # POST-PROCESSING - Get chromatic number from solution
    best_solution = results.first.sample
    usedColors = dict.fromkeys(colors, 0)
    for color in best_solution.values():
        usedColors[color] = 1
    chromatic = sum(usedColors.values())

    toc = time.perf_counter()                       # TIMING
    post_processing_time = toc - tic                # TIMING
            
    # COLLECT RESULTS
    collected = collectResultsDQM(results,
                                realChromaticNumber,
                                chromatic, 
                                QA_time,
                                pre_processing_time, 
                                post_processing_time)


    return collected

def collectResultsDQM(results, realChromaticNumber, chromatic, QA_time, 
                    pre_processing_time, post_processing_time):
    # PERFORMANCE
    qpu_access_time = results.info['qpu_access_time'] # microseconds

    collected = {
        # Accuracy
        'real_chromatic_number': realChromaticNumber,
        'calculated_chromatic_number': chromatic, 

        # Performances
        'QPU_access_time': qpu_access_time / 1000, 
        'total_service_time': QA_time * 1000, 
        'pre_processing': pre_processing_time * 1000, 
        'post_processing': post_processing_time * 1000,
        'from_solver' : 'hybrid_discrete_quadratic_model_version1'
    }

    return collected

def collectResultsBQM(results, realChromaticNumber, chromatic, 
                    QA_time, pre_processing_time, post_processing_time, solverChip):

    # PREFORMANCE
    qpu_access_time = results.info['timing']['qpu_access_time'] # microseconds

    collected = {
        # Accuracy
        'real_chromatic_number': realChromaticNumber,
        'calculated_chromatic_number': chromatic, 

        # Performances
        'QPU_access_time': qpu_access_time / 1000, 
        'total_service_time': QA_time * 1000, 
        'pre_processing': pre_processing_time * 1000, 
        'post_processing': post_processing_time * 1000,

        # Other
        'from_solver' : solverChip
    }

    return collected

def getChromaticNumberBQM(solution, n):
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
