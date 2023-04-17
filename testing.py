from bqm_GCP import solveGCP

nodes = [0,1,2]
edges = [[0,1,0],
        [1,0,1],
        [0,1,0]] 

chromatic_number = solveGCP(nodes, edges)
print(f'Chromatic Number: {chromatic_number}')
