from surfacecode.nodes import ZNode, XNode, DataNode, BaseNode, FlagNode, AncillaNode

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

class HeavyHexLattice(BaseLattice):

    def __init__(self, distance):
        """
        :param int distance: The number of data qubits in the HeavyHexLattice. This must be an odd number.
        """
        assert distance % 2 == 1

        # Formula for number of nodes for HeavyHexLattice given a distance
        self.nodes_num = int((5*distance**2- 2*distance - 1) / 2)
        self.flag_data_column_length = int(distance * 2 - 1)
        self.ancilla_column_length = (distance + 1) // 2

        nodes, graph = self._create_graph(distance)
        super().__init__(nodes, graph)

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
            neighbours = []
            # If we are on data flag node column
            if col % 2 == 0:
                # Add neighbour above
                if itr > 0:
                    neighbours.append(i - 1)
                # Add below neighbour
                if itr < self.flag_data_column_length - 1:
                    neighbours.append(i + 1)

                graph[i] = neighbours
            
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
            neighbours = []
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

                    neighbours.append(target1)
                    neighbours.append(target2)
                    graph[target1].append(i)
                    graph[target2].append(i)


                # If we are on odd ancilla node column
                if col % 4 == 3:
                    if itr == self.ancilla_column_length - 1:
                        target1 = i - self.ancilla_column_length
                        target2 = i + self.flag_data_column_length

                    else:
                        target1 = i - (self.flag_data_column_length - itr * 3 - 1)
                        target2 = i + (self.ancilla_column_length + itr * 3 + 1)

                    neighbours.append(target1)
                    neighbours.append(target2)
                    graph[target1].append(i)
                    graph[target2].append(i)
                
                graph[i] = neighbours

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

