from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from surfacecode.nodes import ZNode, XNode, DataNode, BaseNode, FlagNode, AncillaNode, FlagNode, AncillaNode
from surfacecode.lattice import SquareLattice, HeavyHexLattice, HeavyHexLattice, BaseLattice, Edge
from surfacecode.circuits import ConstrainedQuantumCircuit

class BaseCycle:
    def __init__(self, lattice):
        self.lattice = lattice
        self.num_nodes = len(lattice.nodes)

    def _circuit():
        pass


class SurfaceCodeCycle(BaseCycle):
    """
    QuantumCircuit builder for surface code constrained by the given SquareLattice
    """
    def __init__ (self, lattice):
        assert isinstance(lattice, SquareLattice)
        super().__init__(lattice)

    def _circuit(self, num_cycles=1):
        """
        Returns the surface code QuantumCircuit depending on the number of cycles specified
        :param num_cycles: Number of full cycles the surface code will be runned.
        """
        num_nodes = self.num_nodes
        qc = ConstrainedQuantumCircuit(self.lattice, num_nodes)


        for j in range(num_cycles):
            # For every cycle add a classical register so we can track the changes in the surface code
            qc.add_register(ClassicalRegister(num_nodes))

            # Iterate through names of nodes in square lattice
            # TODO Change lattice.node structure to contain tuples or be a dictionary
            for i in self.lattice.graph.keys():
                node = self.lattice.nodes[i]
                classicalBitLoc = i + j * num_nodes

                # If node is ZNode add measure_z circuit cycle
                if type(node) == ZNode:
                    qc.append(self._measure_z(i), range(num_nodes), [classicalBitLoc])

                # If node is ZNode add measure_x circuit cycle
                elif type(node) == XNode:
                    qc.append(self._measure_x(i), range(num_nodes), [classicalBitLoc])

                # No else statement just in case node is a BaseNode and we strictly want to act on ZNode and XNode

            # Barrier for preventing overlap in gates
            qc.barrier()

        return qc

    def _measure_z(self, qZ):
        """
        Meausure Z quantum circuit cycle that is appended to the QuantumCircuit in the builder
        """
        assert type(qZ) is not list, "You must only give one Measure Z qubit"

        activeNeighbours = []
        for k in self.lattice.graph[qZ]:
            if k.active == True:
                activeNeighbours.append(k.node)

        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 1)

        qc.id([qZ])
        qc.reset([qZ])
        for i in activeNeighbours:
            qc.cx(i, qZ)

        qc.measure([qZ], [0])
        qc.id([qZ])

        return qc.to_instruction(label="measure_z")

    def _measure_x(self, qX):
        """
        Meausure X quantum circuit cycle that is appended to the QuantumCircuit in the builder
        """
        assert type(qX) is not list, "You must only give one Measure X qubit"

        activeNeighbours = []
        for k in self.lattice.graph[qX]:
            if k.active == True:
                activeNeighbours.append(k.node)
        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 1)

        qc.reset([qX])
        qc.h([qX])
        for i in activeNeighbours:
            qc.cx(qX, i)

        qc.h([qX])
        qc.measure([qX], [0])

        return qc.to_instruction(label="measure_x")
    

class HeavyHexCode(BaseCycle):
    def __init__(self, lattice):
        assert isinstance(lattice, HeavyHexLattice)

        super().__init__(lattice)

    def _circuit(self, num_cycles=1):
        """
        Returns the heavy hex code QuantumCircuit depending on the number of cycles specified
        :param num_cycles: Number of full cycles the heavy hex code will be runned.
        """
        num_nodes = self.num_nodes
        qc = ConstrainedQuantumCircuit(self.lattice, num_nodes)


        for j in range(num_cycles):
            # For every cycle add a classical register so we can track the changes in the heavy hex code
            qc.add_register(ClassicalRegister(num_nodes))
            qc.barrier()

            for step in range(1, 12):
            # Iterate through names of nodes in heavy hex lattice
            # TODO Change lattice.node structure to contain tuples or be a dictionary
                if step == 9:
                    qc.barrier()

                for i in self.lattice.graph.keys():
                    node = self.lattice.nodes[i]
                    classicalBitLoc = i + j * num_nodes

                    # If node is AncillaNode add measure_x circuit cycle
                    if type(node) is AncillaNode:
                        neighbour1 = self.lattice.graph[i][0].node
                        neighbour2 = self.lattice.graph[i][1].node

                        if type(self.lattice.nodes[neighbour1]) is DataNode:
                            assert type(self.lattice.nodes[neighbour2]) is DataNode
                            qc = qc.compose(self._measure_x_2_top(i, step), range(num_nodes), [classicalBitLoc])
                            qc = qc.compose(self._measure_x_2_bottom(i, step), range(num_nodes), [classicalBitLoc])

                        if type(self.lattice.nodes[neighbour1]) is FlagNode:
                            classicalBit1 =  neighbour1 + j * num_nodes
                            classicalBit2 =  neighbour2 + j * num_nodes
                            qc = qc.compose(self._measure_x_4(i, step), range(num_nodes), [classicalBit1, classicalBit2, classicalBitLoc])

                    # If node is FlagNode add measure_z circuit cycle
                    if type(node) is FlagNode:
                        qc = qc.compose(self._measure_z_left(i, step), range(num_nodes), [classicalBitLoc])
                        qc = qc.compose(self._measure_z_right(i, step), range(num_nodes), [classicalBitLoc])

                    #     print(neighbour1, neighbour2, i)
                
                # Barrier between steps
                qc.barrier()
                            



                # No else statement just in case node is a BaseNode and we strictly want to act on ZNode and XNode

            # Barrier for preventing overlap in gates
            qc.barrier()

        return qc
    
    def _measure_x_2_top(self, qX, step):
        assert type(qX) is not list,  "You must only give one Measure X qubit"
        assert type(self.lattice.nodes[qX]) is AncillaNode, "The given qubit must be an Ancilla qubit"
        
        dataNeighbours = []
        for k in self.lattice.graph[qX]:
            if k.active == True:
                dataNeighbours.append(k.node)
                        
        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 1)

        # Check if qX is at the top
        if type(self.lattice.nodes[qX - 1]) is not DataNode:
            return qc
        
        if step == 1:
            #Initialize in Z basis
            qc.reset(qX)
            qc.h(qX)
        if step == 4:
            qc.cx(qX, dataNeighbours[1])
        if step == 5:
            qc.cx(qX, dataNeighbours[0])
        if step == 7:
            qc.h([qX])
            qc.measure([qX], 0)

        # return qc.to_instruction(label="measure_x_2")
        return qc
    
    def _measure_x_2_bottom(self, qX, step):
        assert type(qX) is not list,  "You must only give one Measure X qubit"
        assert type(self.lattice.nodes[qX]) is AncillaNode, "The given qubit must be an Ancilla qubit"
        
        dataNeighbours = []
        for k in self.lattice.graph[qX]:
            if k.active == True:
                dataNeighbours.append(k.node)
                        
        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 1)

         # Check if qX is at the bottom
        if type(self.lattice.nodes[qX + 1]) is not DataNode:
            return qc
        
        if step == 5:
            #Initialize in Z basis
            qc.reset(qX)
            qc.h([qX])
        if step == 9:
            qc.cx(qX, dataNeighbours[1])
        if step == 10:
            qc.cx(qX, dataNeighbours[0])
        if step == 11:
            qc.h([qX])
            qc.measure([qX], 0)

        # return qc.to_instruction(label="measure_x_2")
        return qc

    def _measure_x_4(self, qX, step):
        """
        Our ancilla is connected like this:
        D0         D2 
        |          |
        F0 -- A -- F1    or this    D0 -- A -- D1
        |          |
        D1         D3 
        """
        assert type(qX) is not list,  "You must only give one Measure X qubit"
        assert type(self.lattice.nodes[qX]) is AncillaNode, "The given qubit must be an Ancilla qubit"
        
        dataNeighbours = []
        flagNeighbours = []
        for k in self.lattice.graph[qX]:
            if k.active == True:
                flagNeighbours.append(k.node)

        for flag in flagNeighbours:
            for k in self.lattice.graph[flag]:
                # Add neighbours that is not the measure x qubit
                if k.active == True and k.node != qX:
                    dataNeighbours.append(k.node)
                    assert type(self.lattice.nodes[k.node]) is DataNode

        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 3)

        if step == 5:
            #Initialize in X basis
            qc.reset([qX])
            qc.h([qX])
            #Initialize in Z basis
            qc.reset(flagNeighbours[1])
            qc.reset(flagNeighbours[0])
        if step == 6:
            # qc.barrier()
            qc.cx(qX, flagNeighbours[1])

        if step == 7:
            # qc.barrier()
            qc.cx(qX, flagNeighbours[0])
            # I think order matters check Fig 4 of the heavy hex code paper by ibm
            qc.cx(flagNeighbours[1], dataNeighbours[2])
        if step == 8:
            # qc.barrier()
            qc.cx(flagNeighbours[0], dataNeighbours[1])
            qc.cx(flagNeighbours[1], dataNeighbours[3])
        if step == 9:
            # qc.barrier()
            qc.cx(flagNeighbours[0], dataNeighbours[0])
            qc.cx(qX, flagNeighbours[1])
        if step == 10:
            # qc.barrier()
            qc.cx(qX, flagNeighbours[0])
        if step == 11:
            # qc.measure(flagNeighbours[1], [1])
            # # qc.barrier()
            # qc.measure(flagNeighbours[0], [0])
            # Measure in X basis
            qc.h([qX])
            qc.measure([qX], [2])

        # return qc.to_instruction(label="measure_x_4")          
        return qc


    def _measure_z_right(self, qZ, step):
        """
        Our flag qZ is connected like this:
        D0
        |
        F0
        |
        D1
        """
        assert type(qZ) is not list,  "You must only give one Measure Z qubit"
        assert type(self.lattice.nodes[qZ]) is FlagNode, "The given qubit must be an Flag qubit"
        
        dataNeighbours = []
        ancillaNeighbours = []
        for k in self.lattice.graph[qZ]:
            if type(self.lattice.nodes[k.node]) is AncillaNode:
                ancillaNeighbours.append(k.node)

            if k.active == True and type(self.lattice.nodes[k.node]) is not AncillaNode:
                dataNeighbours.append(k.node)
                assert type(self.lattice.nodes[k.node]) is DataNode

        assert len(ancillaNeighbours) <= 1

        
        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 1)

        # Check if qZ is right of ancillas
        if len(ancillaNeighbours) == 0 and qZ > self.lattice.flag_data_column_length:
            return qc
        if len(ancillaNeighbours) > 0 and ancillaNeighbours[0] > qZ:
            return qc
        if step == 1:
            #Initialize in Z basis
            qc.reset(qZ)
            qc.cx(dataNeighbours[0], qZ)
        if step == 2:
            qc.cx(dataNeighbours[1], qZ)
        if step == 4:
            qc.measure([qZ], 0)

        return qc
        # return qc.to_instruction(label="measure_z")
    
    def _measure_z_left(self, qZ, step):
        """
        Our flag qZ is connected like this:
        D0
        |
        F0
        |
        D1
        """
        assert type(qZ) is not list,  "You must only give one Measure Z qubit"
        assert type(self.lattice.nodes[qZ]) is FlagNode, "The given qubit must be an Flag qubit"
        
        dataNeighbours = []
        ancillaNeighbours = []
        for k in self.lattice.graph[qZ]:
            if type(self.lattice.nodes[k.node]) is AncillaNode:
                ancillaNeighbours.append(k.node)

            if k.active == True and type(self.lattice.nodes[k.node]) is not AncillaNode:
                dataNeighbours.append(k.node)
                assert type(self.lattice.nodes[k.node]) is DataNode

        assert len(ancillaNeighbours) <= 1

        
        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 1)

        # Check if qZ is LEFT of ancillas
        if len(ancillaNeighbours) == 0 and qZ < self.lattice.flag_data_column_length:
            return qc
        if len(ancillaNeighbours) > 0 and ancillaNeighbours[0] < qZ:
            return qc
        
        if step == 1:
            #Initialize in Z basis
            qc.reset(qZ)

        if step == 2:
            qc.cx(dataNeighbours[1], qZ)
        if step == 3:
            qc.cx(dataNeighbours[0], qZ)
        if step == 4:
            qc.measure([qZ], 0)

        return qc
        # return qc.to_instruction(label="measure_z")
    
class HeavyHexCode3(BaseCycle):

    def __init__(self):
        num_data = 9
        num_flag = 10
        num_ancilla = 4
        nodes = []
        # Data nodes are in front of list
        for i in range(0, num_data):
            nodes.append(DataNode())

        # Flag nodes are in middle of list
        for i in range(num_data, num_data + num_flag):
            nodes.append(FlagNode())

        # Ancilla nodes are at back of list
        for i in range(num_data + num_flag, num_data + num_flag + num_ancilla):
            nodes.append(AncillaNode())

        graph = {}
        graph[0] = [9, 10]
        graph[1] = [10, 11]
        graph[2] = [11]
        graph[3] = [12, 13]
        graph[4] = [13, 14]
        graph[5] = [14, 15]
        graph[6] = [16]
        graph[7] = [16, 17]
        graph[8] = [17, 18]
        graph[9] = [0, 19]
        graph[10] = [0, 1]
        graph[11] = [1, 2, 20]
        graph[12] = [3, 19]
        graph[13] = [3, 4, 21]
        graph[14] = [4, 5, 20]
        graph[15] = [5, 22]
        graph[16] = [6, 7, 21]
        graph[17] = [7, 8]
        graph[18] = [8, 22]
        graph[19] = [9, 12]
        graph[20] = [11, 14]
        graph[21] = [13, 16]
        graph[22] = [15, 18]

        for i in graph:
            edges = []
            old_list = graph[i]
            for j in old_list:
                edges.append(Edge(j))
            graph[i] = edges    
        
        lattice = BaseLattice(nodes, graph)
        lattice.num_nodes = num_data + num_flag + num_ancilla
        lattice.num_data = num_data
        lattice.num_flag = num_flag
        lattice.num_ancilla = num_ancilla       
        super().__init__(lattice)
    
    def _initialize(self):
        qc = ConstrainedQuantumCircuit(self.lattice, self.lattice.num_nodes)
        initializationRegX = ClassicalRegister(6)
        initializationRegZ = ClassicalRegister(12)
        qc.add_register(initializationRegX)
        qc.add_register(initializationRegZ)

        # # Initialize in 0 state by measuring X gauge
        # qc = qc.compose(self._x_stabilizer(), range(self.lattice.num_nodes), initializationReg)
        itr = 0
        for node in self.lattice.graph:
            if type(self.lattice.nodes[node]) is FlagNode and node not in [9,12,15,18]:
                qc = qc.compose(self.x_gauge(node), range(self.lattice.num_nodes), [initializationRegX[itr]])
                itr += 1
        qc.barrier()

        for i in range(3):
            itr = 0
            for node in self.lattice.graph:
                if type(self.lattice.nodes[node]) is AncillaNode:
                    qc = qc.compose(self.z_gauge(node), range(self.lattice.num_nodes), [initializationRegZ[2*itr + 4], initializationRegZ[2*itr + 5], initializationRegZ[itr]])
                    itr += 1
            qc.barrier()
            itr = 0
            for node in self.lattice.graph:
                if type(self.lattice.nodes[node]) is FlagNode and node not in [9,12,15,18]:
                    qc = qc.compose(self.x_gauge(node), range(self.lattice.num_nodes), [initializationRegX[itr]])
                    itr += 1

        qc.barrier()

        return qc
    
    def _initialize_circuit(self, num_cycles = 1):
        qc = ConstrainedQuantumCircuit(self.lattice, self.lattice.num_nodes)
        initializationRegX = ClassicalRegister(6)
        initializationRegZ = ClassicalRegister(12)
        qc.add_register(initializationRegX)
        qc.add_register(initializationRegZ)

        # # Initialize in 0 state by measuring X gauge
        # qc = qc.compose(self._x_stabilizer(), range(self.lattice.num_nodes), initializationReg)
        itr = 0
        for node in self.lattice.graph:
            if type(self.lattice.nodes[node]) is FlagNode and node not in [9,12,15,18]:
                qc = qc.compose(self.x_gauge(node), range(self.lattice.num_nodes), [initializationRegX[itr]])
                itr += 1
        qc.barrier()

        for i in range(3):
            itr = 0
            for node in self.lattice.graph:
                if type(self.lattice.nodes[node]) is AncillaNode:
                    qc = qc.compose(self.z_gauge(node), range(self.lattice.num_nodes), [initializationRegZ[2*itr + 4], initializationRegZ[2*itr + 5], initializationRegZ[itr]])
                    itr += 1
            qc.barrier()
            itr = 0
            for node in self.lattice.graph:
                if type(self.lattice.nodes[node]) is FlagNode and node not in [9,12,15,18]:
                    qc = qc.compose(self.x_gauge(node), range(self.lattice.num_nodes), [initializationRegX[itr]])
                    itr += 1

        qc.barrier()

        for i in range(num_cycles):
            classicalRegX = ClassicalRegister(6)
            classicalRegZ = ClassicalRegister(4 + 8)
            qc.add_register(classicalRegZ)
            qc.add_register(classicalRegX)

            # qc = qc.compose(self._x_stabilizer(), range(self.lattice.num_nodes), classicalRegX)
            # # qc = qc.compose(self._z_stabilizer(), range(self.lattice.num_nodes), classicalRegZ)
            # qc.barrier()

            itr = 0
            for node in self.lattice.graph:
                if type(self.lattice.nodes[node]) is AncillaNode:
                    qc = qc.compose(self.z_gauge(node), range(self.lattice.num_nodes), [classicalRegZ[2*itr + 4], classicalRegZ[2*itr + 5], classicalRegZ[itr]])
                    itr += 1
            qc.barrier()

            itr = 0
            for node in self.lattice.graph:
                if type(self.lattice.nodes[node]) is FlagNode and node not in [9,12,15,18]:
                    qc = qc.compose(self.x_gauge(node), range(self.lattice.num_nodes), [classicalRegX[itr]])
                    itr += 1

            qc.barrier()

        return qc

    def _circuit(self, num_cycles = 1):
        qc = ConstrainedQuantumCircuit(self.lattice, self.lattice.num_nodes)
        # initializationReg = ClassicalRegister(6)
        # qc.add_register(initializationReg)

        # # # Initialize in 0 state by measuring X gauge
        # # qc = qc.compose(self._x_stabilizer(), range(self.lattice.num_nodes), initializationReg)
        # itr = 0
        # for node in self.lattice.graph:
        #     if type(self.lattice.nodes[node]) is FlagNode and node not in [9,12,15,18]:
        #         qc = qc.compose(self.x_gauge(node), range(self.lattice.num_nodes), [initializationReg[itr]])
        #         itr += 1

        # qc.barrier()

        for i in range(num_cycles):
            classicalRegX = ClassicalRegister(6)
            classicalRegZ = ClassicalRegister(4 + 8)
            qc.add_register(classicalRegZ)
            qc.add_register(classicalRegX)

            # qc = qc.compose(self._x_stabilizer(), range(self.lattice.num_nodes), classicalRegX)
            # # qc = qc.compose(self._z_stabilizer(), range(self.lattice.num_nodes), classicalRegZ)
            # qc.barrier()

            itr = 0
            for node in self.lattice.graph:
                if type(self.lattice.nodes[node]) is AncillaNode:
                    qc = qc.compose(self.z_gauge(node), range(self.lattice.num_nodes), [classicalRegZ[2*itr + 4], classicalRegZ[2*itr + 5], classicalRegZ[itr]])
                    itr += 1
            qc.barrier()

            itr = 0
            for node in self.lattice.graph:
                if type(self.lattice.nodes[node]) is FlagNode and node not in [9,12,15,18]:
                    qc = qc.compose(self.x_gauge(node), range(self.lattice.num_nodes), [classicalRegX[itr]])
                    itr += 1

            qc.barrier()
            
        return qc
    
    def x_gauge(self, flag):
        qc = ConstrainedQuantumCircuit(self.lattice, self.lattice.num_nodes, 1)
        flagNeighbours = []
        for edge in self.lattice.graph[flag]:
            if type(self.lattice.nodes[edge.node]) is DataNode:
                flagNeighbours.append(edge.node)

        qc.reset([flag])
        qc.h([flag])
        for neighbour in flagNeighbours:
            qc.cx(flag, neighbour)
        
        qc.h([flag])
        qc.measure([flag], [0])

        return qc.to_instruction(label="x gauge")
    
    def z_gauge(self, ancilla):
        qc = ConstrainedQuantumCircuit(self.lattice, self.lattice.num_nodes, 3)
        flags = []
        data = []
        for edge in self.lattice.graph[ancilla]:
            if type(self.lattice.nodes[edge.node]) is FlagNode:
                flags.append(edge.node)

        for flag in flags:
            for edge in self.lattice.graph[flag]:
                if type(self.lattice.nodes[edge.node]) is DataNode:
                    data.append(edge.node)

        qc.reset([ancilla])
        qc.h(flags)
        for flag in flags:
            qc.cx(flag, ancilla)

        for flag in flags:
            for d in data:
                qc.cx(d, flag)
        
        for flag in flags:
            qc.cx(flag, ancilla)

        qc.h(flags)
        qc.measure(flags, [0, 1])
        qc.measure([ancilla], [2])

        return qc.to_instruction(label="z gauge")

    
    def _x_stabilizer(self):
        qc = ConstrainedQuantumCircuit(self.lattice, self.lattice.num_nodes, 6)

        flag_nodes = [10, 11, 13, 14, 16, 17]
        qc.h(flag_nodes)

        for i in flag_nodes:
            qc.cx(i, i - 10)

        for i in flag_nodes:
            qc.cx(i, i - 9)

        qc.h(flag_nodes)

        qc.barrier()
        qc.measure(flag_nodes, range(6))
        qc.barrier()

        qc.reset(flag_nodes)
        qc.barrier()

        return qc

    def _z_stabilizer(self):
        qc = ConstrainedQuantumCircuit(self.lattice, self.lattice.num_nodes, 12)

        flag_nodes = [9, 11, 12, 13, 14, 15, 16, 18]
        ancilla_nodes = [19, 20, 21, 22]
        qc.h(flag_nodes)
        for i in ancilla_nodes:
            qc.cx(self.lattice.graph[i][1].node, i)


        for i in ancilla_nodes:
            qc.cx(self.lattice.graph[i][0].node, i)


        for i in [14, 16, 18]:
            qc.cx(i - 10, i)


        for i in [9, 11, 12, 13, 14, 16]:
            qc.cx(i - 9, i)

        for i in ancilla_nodes:
            qc.cx(self.lattice.graph[i][1].node, i)

        for i in ancilla_nodes:
            qc.cx(self.lattice.graph[i][0].node, i)

        qc.h(flag_nodes)

        qc.barrier()
        qc.measure(ancilla_nodes, range(4))
        qc.measure(flag_nodes, range(4, 12))

        qc.barrier()

        qc.reset(flag_nodes + ancilla_nodes)

        qc.barrier()
        return qc