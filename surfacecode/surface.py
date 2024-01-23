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

class ZCycle(BaseCycle):
    def __init__(self):
        pass
 
    def _measure_z(qnum):
        assert qnum >= 1, "You must have at least one measurement qubit."

        qc = QuantumCircuit(qnum, 1)
        qc.id([0])
        qc.reset([0])
        for i in range(1, qnum):
            qc.cx(i, 0)

        qc.measure([0], [0])
        qc.id([0])
        instruction = qc.to_instruction(label="measure_z")
        return instruction

class XCycle(BaseCycle):
    def __init__(self):
        pass


    def _measure_x(qnum):
        assert qnum >= 1, "You must have at least one measurement qubit."

        qc = QuantumCircuit(qnum, 1)
        qc.reset([0])
        qc.h([0])
        for i in range(1, qnum):
            qc.cx(0, i)

        qc.h([0])
        qc.measure([0], [0])
        instruction = qc.to_instruction(label="measure_x")
        return instruction



class Cycle(BaseCycle):
    def __init__(self, lattice):
        self.lattice = lattice

    def _circuit(self, num_cycles=1):
        num_nodes = len(self.lattice.nodes)
        qc = QuantumCircuit(num_nodes, num_cycles * (num_nodes // 2))

        for j in range(num_cycles):
            for i, node in enumerate(self.lattice.nodes):
                connected_qubits = []
                print(self.lattice.graph[i])
                for k in self.lattice.graph[i]:
                    if k.active == True:
                        connected_qubits.append(k.node)
                if type(node) == ZNode:
                    qc.append(ZCycle._measure_z(len(connected_qubits) + 1), [i] + connected_qubits, [i // 2 + j * (num_nodes // 2)])
                elif type(node) == XNode:
                    qc.append(XCycle._measure_x(len(connected_qubits) + 1), [i] + connected_qubits, [i // 2 + j * (num_nodes // 2)])

            qc.barrier()

        return qc

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

        qData = self.lattice.graph[qZ]

        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 1)

        qc.id([qZ])
        qc.reset([qZ])
        for i in qData:
            qc.cx(i, qZ)

        qc.measure([qZ], [0])
        qc.id([qZ])

        return qc.to_instruction(label="measure_z")

    def _measure_x(self, qX):
        """
        Meausure X quantum circuit cycle that is appended to the QuantumCircuit in the builder
        """
        assert type(qX) is not list, "You must only give one Measure X qubit"

        qData = self.lattice.graph[qX]

        qc = ConstrainedQuantumCircuit(self.lattice, self.num_nodes, 1)

        qc.reset([qX])
        qc.h([qX])
        for i in qData:
            qc.cx(qX, i)

        qc.h([qX])
        qc.measure([qX], [0])

        return qc.to_instruction(label="measure_x")