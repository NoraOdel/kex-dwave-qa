from Graph import fileToGraph, Graph, getPossibleGraphs
from GCP import solveGCPbqm, solveGCPdqm
import json 


""" TESTS """
def testAll():
    for density in [0.5, 0.7]:
        for nNodes in range(5,16):

            path = f'./finalTests/{density}/{nNodes}.txt'
            testOne(path, nNodes, density)
        
def testOne(filepath, nNodes, density):
    g = fileToGraph(filepath)

    collectedResultsDQM = solveGCPdqm(g.vertecies, g.adjecency_matrix(), g.chromatic_number)
    collectedResultsBQM = solveGCPbqm(g.vertecies, g.adjecency_matrix(), g.chromatic_number)

    collectedResultsDQM["type"] = 'DQM'
    collectedResultsDQM["number_of_nodes"] = nNodes
    collectedResultsDQM["graph_density"] = density
 
    collectedResultsBQM["type"] = 'BQM'
    collectedResultsBQM["number_of_nodes"] = nNodes
    collectedResultsBQM["graph_density"] = density


    print(collectedResultsDQM)
    print(collectedResultsBQM)

    return 1

            
""" MAIN """
def main():
    testAll()
    #testOne(f'./finalTests/{0.3}/{5}.txt', 5, 0.3)
    return 0


if __name__ == "__main__":
    main()