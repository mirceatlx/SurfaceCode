from surfacecode.lattice import SquareLattice, HeavyHexLattice
from surfacecode.nodes import *

class DirectMap(SquareLattice):
    def __init__ (self, heavyhex):
        self.lattice = heavyhex
        self.nodes = self._get_nodes()
        self.graph = self._get_graph()

    def _get_nodes(self):
        nodes = []
        i = 0
        j = 0
        for node in self.lattice.nodes:
            if type(node) is DataNode:
                if i % 2 == 0:
                    nodes.append(DataNode())
                elif i % 2 == 1 and j % 2 == 0:
                    nodes.append(ZNode())
                elif  i % 2 == 1 and j % 2 == 1:
                    nodes.append(XNode())

                i += 1
                if i % self.lattice.distance == 0:
                    j += 1

            else:
                nodes.append(BaseNode())

        return nodes

    def _get_graph(self):
        graph = {}
        width = self.lattice.distance
        height = self.lattice.distance
        i = 0
        for idx, node in enumerate(self.nodes):
            if type(node) is not BaseNode:
                edges = []
                if i % width != width - 1:
                    edges.append(idx + 2)
                if i + width < width * height:
                    edges.append(idx + self.lattice.flag_data_column_length + self.lattice.ancilla_column_length)
                if i % width > 0:
                    edges.append(idx - 2)
                if i - width >= 0:
                    edges.append(idx - self.lattice.flag_data_column_length - self.lattice.ancilla_column_length)

                graph[idx] = edges
                i += 1
    
        return graph