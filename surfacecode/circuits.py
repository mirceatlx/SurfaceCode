from qiskit import QuantumCircuit, ClassicalRegister
from surfacecode.lattice import SquareLattice
from surfacecode.nodes import ZNode, XNode
import heapq

class CircuitBuilder:
    def __init__(self, lattice):
        self.lattice = lattice
        self.circuit = QuantumCircuit(len(lattice.nodes))

    def _build(self):
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
        path = self.dijkstra(q1, q2)

        for i in range(0, len(path) - 2):
            self.circuit.swap(path[i], path[i + 1])

        self.circuit.cx(path[len(path) - 2], path[len(path) - 1])

        for i in reversed(range(0, len(path) - 2)):
            self.circuit.swap(path[i + 1], path[i])

    def dijkstra(self, start, end):
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
    def __init__ (self, lattice):
        assert isinstance(lattice, SquareLattice)
        super().__init__(lattice)

    def _build(self, num_cycles=1):
        num_nodes = len(self.lattice.nodes)

        for j in range(num_cycles):
            self.add_register(ClassicalRegister(num_nodes))

            print(self.lattice.graph.keys())
            for i in self.lattice.graph.keys():
                node = self.lattice.nodes[i]
                print(f"{i} {node}")
                if type(node) == ZNode:
                    self._measure_z(i, i + j * num_nodes, self.lattice.graph[i])
                elif type(node) == XNode:
                    self._measure_x(i, i + j * num_nodes, self.lattice.graph[i])

            self.barrier()

        return super()._build()

    def _measure_z(self, qZ, c, qData=[]):
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
