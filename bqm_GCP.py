# TODO: Which solver should we run this on?
from dwave.system import DWaveSampler, EmbeddingComposite # = embedding is done by Dwave
from dimod import BinaryQuadraticModel
from QUBO_helper import build_QUBO_matrix

# Constants
NUM_READS = 5                   # Hyperparameter TODO
CHAIN_STRENGTH = 8              # Hyperparameter TODO
ANNEALING_TIME = 1              # Hyperparameter TODO

def solveGCP(nodes: [int], edges: [[int]]):
    """
    Return the approxminated chromatic number of a graph \\
    using Quantum Annealing with a binary quadratic model
    """
    n = len(nodes)

    # CREATE QUBO Matrix
    Q = build_QUBO_matrix(n, nodes, edges)

    # Automatic Embedding in D-wave systems
    sampler = EmbeddingComposite(DWaveSampler())

    # sample_qubo -> Creates bqm from QUBO matrix and runs annealing process
    # returns sampled (approximated) solutions.
    sampleset = sampler.sample_qubo(Q,
                                    num_reads=NUM_READS,
                                    annealing_time=ANNEALING_TIME,
                                    chain_strength=CHAIN_STRENGTH,
                                    label='KEX - Graph Coloring - BQM')

    # Post processing, calculate number of colors from resulting graph coloring
    print(sampleset)
    best_solution = sampleset.first.sample
    n_colors = n
    for value in best_solution.values():
        if (value == 1):
            n_colors -= 1

    # Print approximated chromatic number
    return n_colors

