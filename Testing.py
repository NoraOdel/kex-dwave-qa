from Graph import fileToGraph, Graph, getPossibleGraphs
from bqm_GCP import solveGCP


QA = 'qa'
GATE_BASED = 'gb'


""" TESTS """
def testAll(environment):
    wrong_solutions = 0

    QUBIT_LIMIT = 27 # Based on generated tests
    pairs = getPossibleGraphs(QUBIT_LIMIT) # get possible pairs of nNodes and nEdges, each should correspond to a file in /tests.

    for (nNodes, nEdges) in pairs:
        path = f'./tests/{nNodes}-{nEdges}/1.txt'
        g = fileToGraph(path)
        
        if (environment == QA):
            solution_status = solveWithQA(g)
            wrong_solutions += solution_status
            print('\n\n\n')

            
        elif (environment == GATE_BASED):
            solveWithGateBased(g)
        
    
    if (environment == QA):
        print(f'Number of wrong answers: {wrong_solutions}')
    else:
        print('') # Something else?

def testOne(environment, filepath):
    g = fileToGraph(filepath)

    if (environment == QA):
        solution_status = solveWithQA(g)
            
    elif (environment == GATE_BASED):
        solveWithGateBased(g)



""" SOLVERS """
def solveWithQA(graph: Graph):
    approximated_chromatic_number = solveGCP(graph.vertecies, graph.adjecency_matrix())

    if approximated_chromatic_number == graph.chromatic_number:
        return 0
    else:
        print(f'Quantum Annealing: {approximated_chromatic_number}')
        print(f'Real (exhaustive search): {graph.chromatic_number}')
        return 1

def solveWithGateBased(graph: Graph):
    # TODO: Here?
    return 0



""" MAIN """
def main():
    print("DONE: Changed annealing time to 1 \n\n\n")
    testAll(QA)

    # nNodes, nEdges = 5, 3
    # testOne(QA, f'./tests/6-5/1.txt')
    return 0


if __name__ == "__main__":
    main()