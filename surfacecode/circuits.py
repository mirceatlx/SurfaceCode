from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from surfacecode.lattice import SquareLattice, BaseLattice
from surfacecode.nodes import ZNode, XNode
import heapq
import warnings

class ConstrainedQuantumCircuit(QuantumCircuit):
    """
    A QuantumCircuit Builder that is constrained by the given lattice
    """
    def __init__(self, lattice, *regs, name=None, global_phase=0, metadata=None):
        assert isinstance(lattice, BaseLattice)
        self.lattice = lattice
        
        qnum = 0
        for reg in regs:
            if type(reg) is int:
                qnum = reg
                # Break because for int is always qubit number
                break

            if type(reg) is QuantumRegister:
                qnum += reg.size

        
        # Giver a warning if number qubits and lattice number of nodes do not match
        if qnum != len(lattice.nodes):
            warnings.warn("Number of qubits and number of nodes in lattice do not match")


        super().__init__(*regs, name=name, global_phase=global_phase, metadata=metadata)

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
            self.swap(path[i], path[i + 1])

        # Apply the CNOT gate to q2 and q2's neighbour
        super().cx(path[len(path) - 2], path[len(path) - 1])

        # Reverse the swaps to put the new value at q1
        for i in reversed(range(0, len(path) - 2)):
            self.swap(path[i + 1], path[i])

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

