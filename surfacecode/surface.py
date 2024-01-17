from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from surfacecode.nodes import ZNode, XNode, DataNode, BaseNode


class BaseCycle:
    def __init__(self, lattice):
        self.lattice = lattice

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
                if type(node) == ZNode:
                    qc.append(ZCycle._measure_z(len(self.lattice.graph[i]) + 1), [i] + self.lattice.graph[i], [i // 2 + j * (num_nodes // 2)])
                elif type(node) == XNode:
                    qc.append(XCycle._measure_x(len(self.lattice.graph[i]) + 1), [i] + self.lattice.graph[i], [i // 2 + j * (num_nodes // 2)])

            qc.barrier()

        return qc