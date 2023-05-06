from Graph import fileToGraph, Graph, getPossibleGraphs
from bqm_GCP import solveGCP


QA = 'qa'


""" TESTS """
def testAll(environment):
    for density in [0.3,0.5,0.7]:
        for nNodes in range(5,16):

            path = f'./tests/density/{nNodes}.txt'
            collectedResults = testOne(path, nNodes, density)
        
def testOne(filepath, nNodes, density):
    g = fileToGraph(filepath)
    collectedResults = solveWithQA(g)
    collectedResults['NumberOfNodes'] = nNodes
    collectedResults['GraphDensity'] = density
    print(collectedResults)
    return collectedResults
            

def solveWithQA(g):
    collectedResults = solveGCP(g.vertecies, g.adjecency_matrix(), g.chromatic_number)
    return collectedResults


""" MAIN """
def main():
    #testAll(QA)
    testOne(f'./tests/8-1/1.txt', 8, 0.1)
    return 0


if __name__ == "__main__":
    main()