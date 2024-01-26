import numpy as np
import matplotlib.pyplot as plt
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
        """
        assert num_stabiliezers > 0, num_stabiliezers
        assert num_data_qubits > 0, num_data_qubits

        self.num_stabilizers = num_stabilizers
        self.num_data_qubits = num_data_qubits
        self.lattice_type = lattice_type
        # binary parity check matrix for X and Z syndromes
        self.bpcm = self._create_matrix()


    def _create_matrix(self):
        """
        """
        return np.zeros((self.num_stabilizers, 2 * self.num_data_qubits))

    def _populate(self, lattice: BaseLattice):
        """
        """
        for i, node in enumerate(lattice.nodes):
            edges = lattice.graph[i]
            if isinstance(node, ZNode):
                # NOTE: assume all neighbors are data qubits
                for j in edges:
                    self.bpcm[i][j] = 1

            if isinstance(node, XCode):
                # NOTE: assume all neighbors are data qubits
                for j in edges:
                    self.bpcm[i][j + self.num_data_qubits] = 






    def visualize(self):
        """
        """
        plt.matshow(self.bpcm)
        plt.show()

        return self.bpcm


