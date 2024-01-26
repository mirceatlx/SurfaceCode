from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from surfacecode.circuits import ConstrainedQuantumCircuit

class LQubit:
    #type specifies if the qubit is a Z-cut or X-cut qubit. True for Z-cut, False for X-cut.
    def __init__(self, lattice, m_node, a_node, type):
        self.type = type
        self.m_node = m_node
        self.a_node = a_node
        self.lattice = lattice
        pass

    def initialize(self):
        num_nodes = len(self.lattice.nodes)
        c = ClassicalRegister(1)
        qc = ConstrainedQuantumCircuit(self.lattice, QuantumRegister(num_nodes), c)
        self.lattice._switch_node(self.m_node, False)
        self.lattice._switch_node(self.a_node, False)
        if self.type:
            qc.cx(self.m_node + 1, self.m_node)
            qc.cx(self.m_node - 1, self.m_node)
            qc.cx(self.m_node + self.lattice.width, self.m_node)
            qc.cx(self.m_node - self.lattice.width, self.m_node)
        else:
            qc.h(self.m_node)
            qc.cx(self.m_node, self.m_node + 1)
            qc.cx(self.m_node, self.m_node - 1)
            qc.cx(self.m_node, self.m_node + self.lattice.width)
            qc.cx(self.m_node, self.m_node - self.lattice.width)
            qc.h(self.m_node)
        qc.measure([self.m_node],c)
        # dynamic circuit part, not supported by the simulator
        # with qc.if_test((c, 1)):
        #     route = self.route(self.m_node, self.a_node)
        #     data_qubits = route[1::2]
        #     for i in data_qubits:
        #         if self.type:
        #             qc.x(i)
        #         else:
        #             qc.z(i)
        qc.barrier()
        return qc

    def measure(self):
        num_nodes = len(self.lattice.nodes)
        c = ClassicalRegister(1)
        qc = ConstrainedQuantumCircuit(self.lattice, QuantumRegister(num_nodes), c)
        if self.type:
            qc.cx(self.m_node + 1, self.m_node)
            qc.cx(self.m_node - 1, self.m_node)
            qc.cx(self.m_node + self.lattice.width, self.m_node)
            qc.cx(self.m_node - self.lattice.width, self.m_node)
        else:
            qc.h(self.m_node)
            qc.cx(self.m_node, self.m_node + 1)
            qc.cx(self.m_node, self.m_node - 1)
            qc.cx(self.m_node, self.m_node + self.lattice.width)
            qc.cx(self.m_node, self.m_node - self.lattice.width)
            qc.h(self.m_node)
        qc.measure([self.m_node],c)
        self.lattice._switch_node(self.m_node, True)
        self.lattice._switch_node(self.a_node, True)
        qc.barrier()
        return qc
    
    def alt_initialize(self, cycle):
        route = self.route(self.m_node, self.a_node)
        num_nodes = len(self.lattice.nodes)
        qc = ConstrainedQuantumCircuit(self.lattice, num_nodes, len(route) // 2 + num_nodes // 2)
        reg = 0
        data_qubits = route[1::2]

        for i in route:
            self.lattice._switch_node(i, False)
        qc = qc.compose(cycle._circuit(1), list(range(num_nodes)), list(range(len(route) // 2, len(route) // 2 + num_nodes // 2)))

        for i in data_qubits:
            if self.type:
                qc.h(i)
                qc.measure([i], [reg])
                qc.h(i)
            else:
                qc.measure([i], [reg])
            reg = reg + 1

        for i in route:
            self.lattice._switch_node(i, True)
        self.lattice._switch_node(route[0], False)
        self.lattice._switch_node(route[-1], False)

        qc.barrier()
        return qc

    def alt_measure(self):
        route = self.route(self.m_node, self.a_node)
        num_nodes = len(self.lattice.nodes)
        qc = ConstrainedQuantumCircuit(self.lattice, num_nodes, len(route) // 2)
        reg = 0
        data_qubits = route[1::2]

        for i in data_qubits:
            if self.type:
                qc.h(i)
                qc.measure([i], [reg])
                qc.h(i)
            else:
                qc.measure([i], [reg])
            reg = reg + 1

        for i in route:
            self.lattice._switch_node(i, True)
        qc.barrier()
        return qc

    def circle_gate(self):
        num_nodes = len(self.lattice.nodes)
        qc = ConstrainedQuantumCircuit(self.lattice, num_nodes)
        if self.type:
            qc.z(self.m_node + 1)
            qc.z(self.m_node - 1)
            qc.z(self.m_node + self.lattice.width)
            qc.z(self.m_node - self.lattice.width)
        else:
            qc.x(self.m_node + 1)
            qc.x(self.m_node - 1)
            qc.x(self.m_node + self.lattice.width)
            qc.x(self.m_node - self.lattice.width) 
        qc.barrier()
        return qc

    # direction can be vertical(True) or horisontal(False)
    def line_gate(self):
        num_nodes = len(self.lattice.nodes)
        qc = ConstrainedQuantumCircuit(self.lattice, num_nodes)
        route = self.route(self.m_node, self.a_node)
        data_qubits = route[1::2]
        for i in data_qubits:
            if self.type:
                qc.x(i)
            else:
                qc.z(i)
        qc.barrier()
        return qc
    
    def X(self):
        if self.type:
            return self.line_gate()
        else:
            return self.circle_gate()
    
    def Z(self):
        if self.type:
            return self.circle_gate()
        else:
            return self.line_gate()

    def move_cell(self, cycle, start, end):
        route = self.route(start, end)
        num_nodes = len(self.lattice.nodes)
        qc = ConstrainedQuantumCircuit(self.lattice, num_nodes, 3 * (num_nodes // 2) + len(route) // 2)
        qc = qc.compose(cycle._circuit(1), list(range(num_nodes)), list(range(len(route) // 2, len(route) // 2 + num_nodes // 2)))
        for i in route:
            self.lattice._switch_node(i, False)
        qc = qc.compose(cycle._circuit(1), list(range(num_nodes)), list(range(len(route) // 2 + num_nodes // 2, len(route) // 2 + 2 * (num_nodes // 2))))

        data_qubits = route[1::2]
        register = 0
        for i in data_qubits:
            if self.type:
                qc.h(i)
                qc.measure([i], [register])
                qc.h(i)
            else:
                qc.measure([i], [register])
            register = register + 1

        route.pop()
        for i in route:
            self.lattice._switch_node(i, True)
        qc = qc.compose(cycle._circuit(1), list(range(num_nodes)), list(range(len(route) // 2 + 2 * (num_nodes // 2), len(route) // 2 + 3 * (num_nodes // 2))))
        qc.barrier()
        return qc

    # by default, it will move on the x-axis first if possible, and then move on the y-axis
    # if alt=true, it will move on the y-axis first instead
    def route(self, start, end, alt = False):
        route = []
        width = self.lattice.width
        c_start = (start % width, start // width)
        c_end = (end % width, end // width)
        route.append(c_start)
        if alt:
            while route[-1][1] != c_end[1]:
                if route[-1][1]>c_end[1]:
                    route.append((route[-1][0],route[-1][1]-1))
                else:
                    route.append((route[-1][0],route[-1][1]+1))
            while route[-1][0] != c_end[0]:
                if route[-1][0]>c_end[0]:
                    route.append((route[-1][0]-1,route[-1][1]))
                else:
                    route.append((route[-1][0]+1,route[-1][1]))
        
        while route[-1][0] != c_end[0]:
            if route[-1][0]>c_end[0]:
                route.append((route[-1][0]-1,route[-1][1]))
            else:
                route.append((route[-1][0]+1,route[-1][1]))
        while route[-1][1] != c_end[1]:
            if route[-1][1]>c_end[1]:
                route.append((route[-1][0],route[-1][1]-1))
            else:
                route.append((route[-1][0],route[-1][1]+1))
        return list(map(lambda x : x[0] + width * x[1],route))
