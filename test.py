from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from surfacecode.lattice import *
from surfacecode.circuits import *
from surfacecode.surface import *
from surfacecode.logical_qubit import *
from surfacecode.parser import *
from surfacecode.adapter import *
from surfacecode.nodes import *

def surface_code_five_cycles():
    lattice = SquareLattice(3,3)
    num_nodes = len(lattice.nodes)
    surfacecode = SurfaceCodeCycle(lattice)

    qc = surfacecode._circuit(5)
    qc.add_register(ClassicalRegister(num_nodes))
    qc.append(surfacecode._circuit(), range(num_nodes), range(5*num_nodes, 6* num_nodes))

    aersim = AerSimulator()
    built = transpile(qc, aersim)
    job = aersim.run(built, shots = 1)
    result = job.result()

    measurements = list(result.get_counts().keys())

    assert len(measurements) == 1
    
    for i in measurements[0].split(" "):
        assert i == measurements[0].split(" ")[0]

if __name__ == "__main__":
    surface_code_five_cycles()