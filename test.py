import sys
import tracemalloc

from rdflib import Graph

tracemalloc.start()

g = Graph()
g.parse(file=sys.stdin, format="nt")

# displaying the memory
print(tracemalloc.get_traced_memory())

# stopping the library
tracemalloc.stop()
