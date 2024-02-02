import numpy as np
import matplotlib.pyplot as plt
import pymatching

from surfacecode.lattice import BaseLattice
from surfacecode.nodes import ZNode, XNode

"""
Based on https://arxiv.org/pdf/2105.13082.pdf
"""


class ParityCheckMatrix:
    """
    Binary Parity Check Matrix for Minimum Weight Perfect Matching algorithm.
    (X|Z)
    """
    # TODO: take in consideration both surface code and heavy hex code


    def __init__(self, num_stabilizers: int, num_data_qubits: int, lattice_type: str = "surface"):
        """
        num_stabilizers: number of stabilizers in the code (X + Z) stabilizers
        num_data_qubits: number of data qubits in the code
        lattice_type: type of lattice code (surface or heavy hex)
        """
        assert num_stabilizers > 0, num_stabilizers
        assert num_data_qubits > 0, num_data_qubits

        self.num_stabilizers = num_stabilizers
        self.num_data_qubits = num_data_qubits
        self.lattice_type = lattice_type
        # binary parity check matrix for X and Z syndromes
        self.bpcm = self._create_matrix()


    def _create_matrix(self):
        """
        Creates an empty binary parity check matrix for the given lattice type.
        """
        return np.zeros((self.num_stabilizers, 2 * self.num_data_qubits))

    def _populate(self, lattice: BaseLattice):
        """
        Populates the binary parity check matrix with the given lattice.
        """
        for i, node in enumerate(lattice.nodes):
            edges = lattice.graph[i]
            if isinstance(node, ZNode):
                # NOTE: assume all neighbors are data qubits
                for edge in edges:
                    self.bpcm[node.idx + lattice.x_counter][lattice.nodes[edge.node].idx] = 1

            if isinstance(node, XNode):
                # NOTE: assume all neighbors are data qubits
                for edge in edges:
                    self.bpcm[node.idx][lattice.nodes[edge.node].idx + self.num_data_qubits] = 1

        return self.bpcm


    def visualize(self):
        """
        Visualize the binary parity check matrix.
        """
        plt.matshow(self.bpcm)
        plt.show()

        return self.bpcm



class ErrorCorrection:
    """
    """

    def __init__(self, mparity: ParityCheckMatrix):
        self.mparity = mparity

    def analyze(self, states: np.ndarray):
        """
        """
        assert states.shape[1] == self.mparity.bpcm.shape[0], f"First dim of a states should match the first dim of the parity matrix, {states[0].shape[0]} != {self.mparity.shape[0]}"
        qstate = states[0] # quiescent state
        matching = pymatching.Matching(self.mparity.bpcm)
        errors = np.zeros(self.mparity.bpcm.shape[1], dtype=np.uint8)
        for i in range(states.shape[0]):
            state = states[i]
            syndrome = (state + qstate) % 2
            prediction = matching.decode(syndrome)
            errors = (errors + prediction) % 2
            qstate = state

        return errors

