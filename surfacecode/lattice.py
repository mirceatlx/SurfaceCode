from surfacecode.nodes import ZNode, XNode, DataNode, BaseNode, FlagNode, AncillaNode

class BaseLattice:

    def __init__(self, nodes, graph):
       self.nodes = nodes
       self.graph = graph

class Edge:
    def __init__(self, node, active = True):
        self.node = node
        self.active = active

class SquareLattice(BaseLattice):
    """
    Class for Square Lattice
    N -- N -- N -- N
    |    |    |    |
    N -- N -- N -- N
    |    |    |    |
    N -- N -- N -- N
    |    |    |    |
    N -- N -- N -- N
    """

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

        nodes = [BaseNode(-1) for i in range(width * height)]
        j = 1
        z_counter = x_counter = d_counter = 0
        for i in range(width * height):
            if i >= width * j:
                j += 1
            # if i < width * j:
            if i % 2 == 1:
                if j % 2 == 1:
                    nodes[i] = ZNode(z_counter)
                    z_counter += 1
                else:
                    nodes[i] = XNode(x_counter)
                    x_counter += 1
            else:
                nodes[i] = DataNode(d_counter)
                d_counter += 1

        self.z_counter = z_counter
        self.x_counter = x_counter
        self.d_counter = d_counter
            
            
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

class HeavyHexLattice(BaseLattice):
    """
    Class for Heavy Hex Lattice where D is data node, A is ancilla node, F is flag node
    D -- A -- D         D -- A -- D         D
    |         |         |         |         |
    F         F -- A -- F         F -- A -- F
    |         |         |         |         |
    D         D         D         D         D
    |         |         |         |         |
    F -- A -- F         F -- A -- F         F
    |         |         |         |         |
    D         D         D         D         D
    |         |         |         |         |
    F         F -- A -- F         F -- A -- F
    |         |         |         |         |
    D         D         D         D         D
    |         |         |         |         |
    F -- A -- F         F -- A -- F         F
    |         |         |         |         |
    D         D -- A -- D         D -- A -- D
    """

    def __init__(self, distance):
        """
        :param int distance: The number of data qubits in the HeavyHexLattice. This must be an odd number.
        """
        assert distance % 2 == 1

        # Formula for number of nodes for HeavyHexLattice given a distance
        self.distance = distance
        self.nodes_num = int((5*distance**2- 2*distance - 1) / 2)
        self.flag_data_column_length = int(distance * 2 - 1)
        self.ancilla_column_length = (distance + 1) // 2

        # Nodes indices go from up down then left to right
        nodes, graph = self._create_graph(distance)
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

    def _create_graph(self, distance):
        """
        Method that creates the heavy hex graph
        :param distance: distance of heavy hex code must be an odd number
        """
        assert distance % 2 == 1
        # Formula for number of nodes for HeavyHexLattice given a distance
        nodes = self._create_nodes()
        graph = self._connect_data_flag()
        graph = self._connect_ancilla(graph)
        
        return nodes, graph

    def _create_nodes(self):
        """
        Method that creates nodes and assign them their index in the array
        """
        nodes = []
        # Add data, flag, ancilla nodes
        col = 0
        itr = 0
        for i in range(self.nodes_num):
            # If we are on data flag node column
            if col % 2 == 0:
                if itr % 2 == 0:
                    nodes.append(DataNode())
                else:
                    nodes.append(FlagNode())

                # If we reach the end of the column, increment col and reset itr values
                if itr == self.flag_data_column_length - 1:
                    col += 1
                    itr = 0
                    continue
                
            #If we are on ancilla node column
            if col % 2 == 1:
                nodes.append(AncillaNode())

                # If we reach the end of the column, increment col and reset itr values
                if itr == self.ancilla_column_length - 1:
                    itr = 0
                    col += 1
                    continue

            itr += 1
        
        return nodes
    
    def _connect_data_flag(self):
        """
        Assigns edges to data and flag nodes and returns a the dictionary graph
        """
        graph = {}
        col = 0
        itr = 0
        # Connect data and flag nodes
        for i in range(self.nodes_num):
            edges = []
            # If we are on data flag node column
            if col % 2 == 0:
                # Add neighbour above
                if itr > 0:
                    edges.append(Edge(i - 1))
                # Add below neighbour
                if itr < self.flag_data_column_length - 1:
                    edges.append(Edge(i + 1))

                graph[i] = edges
            
            # If we reach the end of the data flag column, increment col and reset itr values
            if itr == self.flag_data_column_length - 1 and col % 2 == 0:
                col += 1
                itr = 0
                continue

            # If we reach the end of the ancilla column, increment col and reset itr values
            if itr == self.ancilla_column_length - 1 and col % 2 == 1:
                itr = 0
                col += 1
                continue

            itr += 1
        
        return graph
    
    def _connect_ancilla(self, graph):
        """
        Connects ancilla nodes to data and flag nodes and vice versa.
        :param graph: Graph of nodes where it is assumed data and flag nodes are connected
        """
        col = 0
        itr = 0
        # Connect ancilla nodes to data, flag nodes and vice versa
        for i in range(self.nodes_num):
            edges = []
            #If we are on ancilla node column
            if col % 2 == 1:
                # If we are on even ancilla node column (start counting from zero)
                if col % 4 == 1:
                    if itr == 0:
                        target1 = i - self.flag_data_column_length
                        target2 = i + self.ancilla_column_length

                    else:
                        target1 = i - (self.flag_data_column_length - itr * 3 + 1)
                        target2 = i + (self.ancilla_column_length + itr * 3 - 1)

                    edges.append(Edge(target1))
                    edges.append(Edge(target2))
                    graph[target1].append(Edge(i))
                    graph[target2].append(Edge(i))


                # If we are on odd ancilla node column
                if col % 4 == 3:
                    if itr == self.ancilla_column_length - 1:
                        target1 = i - self.ancilla_column_length
                        target2 = i + self.flag_data_column_length

                    else:
                        target1 = i - (self.flag_data_column_length - itr * 3 - 1)
                        target2 = i + (self.ancilla_column_length + itr * 3 + 1)

                    edges.append(Edge(target1))
                    edges.append(Edge(target2))
                    graph[target1].append(Edge(i))
                    graph[target2].append(Edge(i))
                
                graph[i] = edges

            # If we reach the end of the data flag column, increment col and reset itr values
            if itr == self.flag_data_column_length - 1 and col % 2 == 0:
                col += 1
                itr = 0
                continue

            # If we reach the end of the ancilla column, increment col and reset itr values
            if itr == self.ancilla_column_length - 1 and col % 2 == 1:
                itr = 0
                col += 1
                continue
                
            itr += 1

        return graph

