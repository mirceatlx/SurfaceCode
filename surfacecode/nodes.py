"""
Types of nodes in stabilizer code.
"""

class BaseNode:
    def __init__(self, idx: int):
        """
        """
        self.idx = idx


class ZNode(BaseNode):
    """
    Measure-Z qubit.
    """
    def __init__(self, idx: int):
        super().__init__(idx)

class XNode(BaseNode):
    """
    Measure-X qubit.
    """
    def __init__(self, idx: int):
        super().__init__(idx)

class DataNode(BaseNode):
    """
    Data qubit.
    """
    def __init__(self, idx: int):
        super().__init__(idx)

class FlagNode(BaseNode):
    """
    Flag qubit.
    """
    def __init__(self, idx: int):
        super().__init__(idx)

class AncillaNode(BaseNode):
    """
    Ancilla qubit.
    """
    def _init__(self, idx: int):
        super().__init__(idx)
