from qiskit import QuantumCircuit
import heapq

class CircuitBuilder:
    def __init__(self, lattice):
        self.lattice = lattice
        self.circuit = QuantumCircuit(len(lattice.nodes), len(lattice.nodes))


    def _build(self):
        return self.circuit
    
    def h(self, q):
        self.circuit.h(q)

    def x(self, q):
        self.circuit.x(q)

    def z(self, q):
        self.circuit.z(q)

    def y(self, q):
        self.circuit.y(q)

    def cx(self, q1, q2):
        path = self.dijkstra(q1, q2)

        for i in range(0, len(path) - 2):
            self.circuit.swap(path[i], path[i + 1])

        self.circuit.cx(path[len(path) - 2], path[len(path) - 1])

        for i in reversed(range(0, len(path) - 2)):
            self.circuit.swap(path[i + 1], path[i])

    def dijkstra(self, start, end):
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
