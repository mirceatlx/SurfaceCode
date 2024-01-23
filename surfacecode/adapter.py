from surfacecode.lattice import SquareLattice, HeavyHexLattice, Edge
from surfacecode.nodes import *

class DirectMap(SquareLattice):
    """
    An adapter that converts HeavyHexLattice to a SquareLattice using direct mapping
    """
    def __init__ (self, heavyhex):
        self.lattice = heavyhex
        self.nodes = self._get_nodes()
        self.graph = self._get_graph()


    def _get_nodes(self):
        """
        Returns list of node types where indices correspond to the name of the node. 
        If the node type is BaseNode it is essentially not part of the SquareLattice
        """
        nodes = []
        i = 0   # Node counter for nodes in square lattice
        j = 0   # Counter for moving from one column to the next
        for node in self.lattice.nodes:
            # Only DataNodes in HeavyHexLattice are part of the new SquareLattice
            if type(node) is DataNode:
                if i % 2 == 0:
                    nodes.append(DataNode())
                elif i % 2 == 1 and j % 2 == 0:
                    nodes.append(ZNode())
                elif  i % 2 == 1 and j % 2 == 1:
                    nodes.append(XNode())

                i += 1
                # Checks if we have reached the bottom of the heavy hex column
                if i % self.lattice.distance == 0:
                    j += 1

            # Adds a "useless" node. This is needed because indices of self.nodes correspond to the name of the node.
            # Furthermore the name of the node must be conserved during this mapping
            else:
                nodes.append(BaseNode())

        return nodes

    def _get_graph(self):
        """
        Method that returns a graph dictionary that contains the neighbours of the nodes in this "SquareLattice"
        Note that these neighbours are mapped and do not correspond to the true neighbours from the HeavyHexLattice
        """
        graph = {}
        width = self.lattice.distance
        height = self.lattice.distance
        
        i = 0    # Counter for nodes in square lattice

        for idx, node in enumerate(self.nodes):
            # As long as the node is no the "useless" node, give it neighbours and add them to the graph
            if type(node) is not BaseNode:
                edges = []
                # If node is not at bottom side
                if i % width != width - 1:
                    edges.append(Edge(idx + 2))
                # If node is not at right side
                if i + width < width * height:
                    edges.append(Edge(idx + self.lattice.flag_data_column_length + self.lattice.ancilla_column_length))
                # If node is not at top side
                if i % width > 0:
                    edges.append(Edge(idx - 2))
                # If node is not at left side
                if i - width >= 0:
                    edges.append(Edge(idx - self.lattice.flag_data_column_length - self.lattice.ancilla_column_length))

                graph[idx] = edges
                i += 1
    
        return graph