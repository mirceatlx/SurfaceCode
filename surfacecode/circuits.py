from qiskit import QuantumCircuit, ClassicalRegister
from surfacecode.lattice import SquareLattice
from surfacecode.nodes import ZNode, XNode
import heapq

class CircuitBuilder:
    """
    A QuantumCircuit Builder that is constrained by the given lattice
    """
    def __init__(self, lattice):
        self.lattice = lattice
        self.circuit = QuantumCircuit(len(lattice.nodes))

    def _build(self):
        """
        Returns the QuantumCircuit that was being built
        """
        return self.circuit
    
    def barrier(self):
        self.circuit.barrier()
    
    def id(self, q):
        self.circuit.id(q)

    def reset(self, q):
        self.circuit.reset(q)

    def h(self, q):
        self.circuit.h(q)

    def x(self, q):
        self.circuit.x(q)

    def z(self, q):
        self.circuit.z(q)

    def y(self, q):
        self.circuit.y(q)

    def measure(self, q, c):
        self.circuit.measure(q, c)

    def add_register(self, register):
        self.circuit.add_register(register)

    def cx(self, q1, q2):
        """
        CNOT gate applies CNOT only to neighbouring qubits, if not a series of swaps must be applied first.
        :param q1: Name of qubit 1 (integer)
        :param q2: Name of qubit 2 (integer)
        """

        # Find the shortest path between the 2 target qubits. If they are neighbouring a path of length 2 is returned
        path = self.dijkstra(q1, q2)

        # For every node in between q1 and q2, apply swap until the data of q1 is next to q2
        for i in range(0, len(path) - 2):
            self.circuit.swap(path[i], path[i + 1])

        # Apply the CNOT gate to q2 and q2's neighbour
        self.circuit.cx(path[len(path) - 2], path[len(path) - 1])

        # Reverse the swaps to put the new value at q1
        for i in reversed(range(0, len(path) - 2)):
            self.circuit.swap(path[i + 1], path[i])

    def dijkstra(self, start, end):
        """
        Dijkstra's algorithm to find the shortest path between start and end qubits from the lattice
        :param start: Name of start qubit (integer)
        :param end: Name of end qubit (integer)
        """
        try:
            # See if the lattice is actually an adapter
            graph = self.lattice.lattice.graph
        except: 
            graph = self.lattice.graph

        # Initialize distances with infinity for all nodes except the start node
        distances = {node: float('infinity') for node in graph}
        distances[start] = 0
        
        # Use a priority queue (heap) to keep track of the nodes with the smallest distances
        priority_queue = [(0, start)]

        # Initialize a dictionary to store the paths
        paths = {node: [] for node in graph}

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            # Check if the current distance is smaller than the stored distance for the current node
            if current_distance > distances[current_node]:
                continue

            # Explore neighbors of the current node
            for neighbor in graph[current_node]:
                weight = 1
                distance = current_distance + weight

                # If a shorter path is found, update the distance and path, and push it to the priority queue
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    paths[neighbor] = paths[current_node] + [current_node]
                    heapq.heappush(priority_queue, (distance, neighbor))

        # Construct the paths for each node
        final_paths = {node: path + [node] for node, path in paths.items()}

        return final_paths[end]

class SurfaceCodeBuilder(CircuitBuilder):
    """
    QuantumCircuit builder for surface code constrained by the given SquareLattice
    """
    def __init__ (self, lattice):
        assert isinstance(lattice, SquareLattice)
        super().__init__(lattice)

    def _build(self, num_cycles=1):
        """
        Returns the surface code QuantumCircuit depending on the number of cycles specified
        :param num_cycles: Number of full cycles the surface code will be runned.
        """
        num_nodes = len(self.lattice.nodes)

        for j in range(num_cycles):
            # For every cycle add a classical register so we can track the changes in the surface code
            self.add_register(ClassicalRegister(num_nodes))

            # Iterate through names of nodes in square lattice
            # TODO Change lattice.node structure to contain tuples or be a dictionary
            for i in self.lattice.graph.keys():
                node = self.lattice.nodes[i]

                # If node is ZNode add measure_z circuit cycle
                if type(node) == ZNode:
                    self._measure_z(i, i + j * num_nodes, self.lattice.graph[i])

                # If node is ZNode add measure_x circuit cycle
                elif type(node) == XNode:
                    self._measure_x(i, i + j * num_nodes, self.lattice.graph[i])

                # No else statement just in case node is a BaseNode and we strictly want to act on ZNode and XNode

            # Barrier for preventing overlap in gates
            self.barrier()

        return super()._build()

    def _measure_z(self, qZ, c, qData=[]):
        """
        Meausure Z quantum circuit cycle that is appended to the QuantumCircuit in the builder
        """
        assert type(qZ) is not list, "You must only give one Measure Z qubit"
        assert type(qData) is list, "You must give a list of data qubits"

        self.barrier()
        self.id([qZ])
        self.reset([qZ])
        for i in qData:
            self.cx(i, qZ)

        self.measure([qZ], [c])
        self.id([qZ])
        self.barrier()

    def _measure_x(self, qX, c, qData=[]):
        """
        Meausure X quantum circuit cycle that is appended to the QuantumCircuit in the builder
        """
        assert type(qX) is not list, "You must only give one Measure X qubit"
        assert type(qData) is list, "You must give a list of data qubits"
        
        self.barrier()
        self.reset([qX])
        self.h([qX])
        for i in qData:
            self.cx(qX, i)

        self.h([qX])
        self.measure([qX], [c])
        self.barrier()
