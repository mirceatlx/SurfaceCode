from surfacecode.nodes import ZNode, XNode, DataNode, BaseNode

class BaseLattice:

    def __init__(self, nodes, graph):
       self.nodes = nodes
       self.graph = graph

class SquareLattice(BaseLattice):

    def __init__(self, width, height):

        nodes, graph = self._create_graph(width, height)
        super().__init__(nodes, graph)

    def _create_graph(self, width, height):
        # data qubits in the corners of the lattice
        #TODO: define what borders you want
        assert width % 2 == 1
        assert height % 2 == 1

        nodes = [DataNode() if i % 2 == 0 else BaseNode() for i in range(width*height)]
        j = 1
        for i in range(1, width*height, 2):
            if i >= width *j:
                j += 1
            # if i < width * j:
            nodes[i] = ZNode() if j % 2 == 1 else XNode()
            
            
        graph = {}
        for i in range(len(nodes)):
            edges = []
            if i % width != width - 1:
                edges.append(i + 1)
            if i + width < width * height:
                edges.append(i + width)
            if i % width > 0:
                edges.append(i - 1)
            if i - width >= 0:
                edges.append(i - width)

            graph[i] = edges

        return nodes, graph