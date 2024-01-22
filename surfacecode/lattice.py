from surfacecode.nodes import ZNode, XNode, DataNode, BaseNode

class BaseLattice:

    def __init__(self, nodes, graph):
       self.nodes = nodes
       self.graph = graph

class Edge:
    def __init__(self, node, active = True):
        self.node = node
        self.active = active

class SquareLattice(BaseLattice):

    def __init__(self, width, height):

        nodes, graph = self._create_graph(width, height)
        self.width = width
        self.height = height
        super().__init__(nodes, graph)

    def _switch_node(self, t_node, switch):
        temp1 = []
        for i in self.graph[t_node]:
            temp1.append(Edge(i.node, switch))
            temp2 = []
            for e in self.graph[i.node]:
                if e.node == t_node:
                    temp2.append(Edge(t_node, switch))
                else:
                    temp2.append(e)
            self.graph[i.node] = temp2
        self.graph[t_node]=temp1
        return

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
                edges.append(Edge(i + 1))
            if i + width < width * height:
                edges.append(Edge(i + width))
            if i % width > 0:
                edges.append(Edge(i - 1))
            if i - width >= 0:
                edges.append(Edge(i - width))

            graph[i] = edges

        return nodes, graph