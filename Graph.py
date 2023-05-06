import numpy as np

class Graph:
    def __init__(self, nVertecies: int, edges: np.array, chromatic_number: int):
        self.vertecies = list(range(nVertecies))
        self.nVertecies = nVertecies
        self.edges = edges
        self.chromatic_number = chromatic_number

    def adjecency_matrix(self):
        matrix = []
        for _ in range(self.nVertecies):
            li = []
            for _ in range(self.nVertecies):
                li.append(0)
            matrix.append(li)

        for edge in self.edges:
            i = edge[0]
            j = edge[1]
            matrix[i][j] = 1
            matrix[j][i] = 1

        return matrix
        

    def valid_coloring(self, coloring):
        for e in self.edges:
            if coloring[e[0]] == coloring[e[1]]:
                return False
            
        return True

def fileToGraph(filepath):
    f = open(filepath, "r")
    content = f.readlines()

    chromatic = int(content[0])
    nNodes = int(content[1])
    # nEdges = int(content[2])
    content[-1] = content[-1].replace("\n", "")

    edges = []
    for edge in content[3:]:
        [x, y] = edge.split()
        edges.append([int(x), int(y)])

    return Graph(nNodes, np.array(edges), chromatic)
        
    

# TODO: Scrap?
def getPossibleGraphs(qubit_limit):
    def enough_qubits(n, e):
        return int(n*np.ceil(np.log2(n))+e+1) <= qubit_limit

    def graph_exists(n, e):
        return (((n**2)-n) / 2) >= e

    pairs = []
    for n in range(1, 10):
        for e in range(1, 31):
            if enough_qubits(n, e) and graph_exists(n, e):
                pairs.append((n, e))

    return pairs

    

    

        

