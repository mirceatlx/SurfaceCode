from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from surfacecode.nodes import ZNode, XNode, DataNode, BaseNode
from surfacecode.lattice import SquareLattice
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
        for k in self.lattice.graph[i]:
            if k.active == True:
                activeNeighbours.append(k.node)

        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 1)

        qc.id([qZ])
        qc.reset([qZ])
        for i in activeNeighbours:
            qc.cx(i.node, qZ)

        qc.measure([qZ], [0])
        qc.id([qZ])

        return qc.to_instruction(label="measure_z")

    def _measure_x(self, qX):
        """
        Meausure X quantum circuit cycle that is appended to the QuantumCircuit in the builder
        """
        assert type(qX) is not list, "You must only give one Measure X qubit"

        activeNeighbours = []
        for k in self.lattice.graph[i]:
            if k.active == True:
                activeNeighbours.append(k.node)
        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 1)

        qc.reset([qX])
        qc.h([qX])
        for i in activeNeighbours:
            qc.cx(qX, i.node)

        qc.h([qX])
        qc.measure([qX], [0])

        return qc.to_instruction(label="measure_x")