from Graph import fileToGraph, Graph, getPossibleGraphs
from GCP import solveGCPbqm, solveGCPdqm


""" TESTS """
def testAll():
    for density in [0.3,0.5,0.7]:
        for nNodes in range(5,16):

            path = f'./tests/density/{nNodes}.txt'
            testOne(path, nNodes, density)
        
def testOne(filepath, nNodes, density):
    g = fileToGraph(filepath)

    collectedResultsDQM = solveGCPdqm(g.vertecies, g.adjecency_matrix(), g.chromatic_number)
    collectedResultsBQM = solveGCPbqm(g.vertecies, g.adjecency_matrix(), g.chromatic_number)

    collectedResultsDQM['type'] = 'DQM'
    collectedResultsDQM['number_of_nodes'] = nNodes
    collectedResultsDQM['graph_density'] = density
 
    collectedResultsBQM['type'] = 'BQM'
    collectedResultsBQM['number_of_nodes'] = nNodes
    collectedResultsBQM['graph_density'] = density

    print(collectedResultsDQM)
    print(collectedResultsBQM)

    return 1

            
""" MAIN """
def main():
    #testAll()
    testOne(f'./tests/5-3/1.txt', 15, 0.7)
    return 0


if __name__ == "__main__":
    main()