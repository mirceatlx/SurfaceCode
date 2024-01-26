from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from surfacecode.lattice import *
from surfacecode.circuits import *
from surfacecode.surface import *
from surfacecode.logical_qubit import *
from surfacecode.parser import *
from surfacecode.adapter import *
from surfacecode.nodes import *
import time

def surface_code_five_cycles():
    print("Running test surface_code_five_cycles")
    startTime = time.time()
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

    print(f"Done in {time.time() - startTime}")

def surface_code_detects_one_x_error():
    print("Running test surface_code_detects_one_x_error")
    startTime = time.time()

    lattice = SquareLattice(5, 5)
    num_nodes = len(lattice.nodes)
    surfacecode = SurfaceCodeCycle(lattice)
    N =1

    qc = surfacecode._circuit(N)
    qc.add_register(ClassicalRegister(num_nodes))
    qc.x([6])
    qc.append(surfacecode._circuit(), range(num_nodes), range(N*num_nodes, (N+1)* num_nodes))


    aersim = AerSimulator(method="stabilizer")
    built = transpile(qc, aersim)
    job = aersim.run(built, shots = 1)
    result = job.result()


    measurements = list(result.get_counts().keys())
    prev = ""
    error_detected = []
    for i in measurements[0].split(" "):
        i = i[::-1]
        for idx, j in enumerate(i):
            if prev == "":
                prev = i
                break

            if j != prev[idx]:
                error_detected.append(idx)
                # print(f"Disimilarity at measurement qubit {len(prev) - idx - 1}")
        
    assert len(error_detected) == 2
    assert 1 in error_detected
    assert 11 in error_detected
    
    print(f"Done in {time.time() - startTime}")


def surface_code_detects_one_z_error():
    print("Running test surface_code_detects_one_z_error")
    startTime = time.time()
    lattice = SquareLattice(5, 5)
    num_nodes = len(lattice.nodes)
    surfacecode = SurfaceCodeCycle(lattice)
    N =1

    qc = surfacecode._circuit(N)
    qc.add_register(ClassicalRegister(num_nodes))
    qc.z([6])
    qc.append(surfacecode._circuit(), range(num_nodes), range(N*num_nodes, (N+1)* num_nodes))


    aersim = AerSimulator(method="stabilizer")
    built = transpile(qc, aersim)
    job = aersim.run(built, shots = 1)
    result = job.result()


    measurements = list(result.get_counts().keys())
    prev = ""
    error_detected = []
    for i in measurements[0].split(" "):
        i = i[::-1]
        for idx, j in enumerate(i):
            if prev == "":
                prev = i
                break

            if j != prev[idx]:
                error_detected.append(idx)
                # print(f"Disimilarity at measurement qubit {len(prev) - idx - 1}")
        
    assert len(error_detected) == 2
    assert 7 in error_detected
    assert 5 in error_detected

    print(f"Done in {time.time() - startTime}")

def heavy_hex_lattice_direct_mapping_surface_code_five_cycles():
    print("Running test heavy_hex_lattice_direct_mapping_surface_code_five_cycles")
    startTime = time.time()

    lattice = HeavyHexLattice(5)
    square = DirectMap(lattice)
    num_nodes = len(square.nodes)
    surfacecode = SurfaceCodeCycle(square)

    qc = surfacecode._circuit(5)
    qc.add_register(ClassicalRegister(num_nodes))
    qc.append(surfacecode._circuit(), range(num_nodes), range(5*num_nodes, 6* num_nodes))

    aersim = AerSimulator(method="stabilizer")
    built = transpile(qc, aersim)
    job = aersim.run(built, shots = 1)
    result = job.result()

    measurements = list(result.get_counts().keys())

    assert len(measurements) == 1
    
    for i in measurements[0].split(" "):
        assert i == measurements[0].split(" ")[0]

    print(f"Done in {time.time() - startTime}")

def heavy_hex_code_five_cycles():
    print("Running test heavy_hex_code_five_cycles")
    startTime = time.time()

    lattice = HeavyHexLattice(5)
    num_nodes = len(lattice.nodes)
    heavyhexcode = HeavyHexCode(lattice)
    qc = heavyhexcode._circuit(5)

    aersim = AerSimulator(method="stabilizer")
    built = transpile(qc, aersim)
    job = aersim.run(built, shots = 1)
    result = job.result()
    
    measurements = list(result.get_counts().keys())
    assert len(measurements) == 1
    
    for i in measurements[0].split(" "):
        assert i == measurements[0].split(" ")[0]

    print(f"Done in {time.time() - startTime}")


if __name__ == "__main__":
    surface_code_five_cycles()
    heavy_hex_lattice_direct_mapping_surface_code_five_cycles()
    surface_code_detects_one_x_error()
    heavy_hex_code_five_cycles()

