import math
import numpy as np

from projectq import MainEngine
from projectq.backends import CircuitDrawer, Simulator, RotationDecomposition
from projectq.ops import H, Z, X, Measure, All, R, CNOT, Rz, T, S
from projectq.meta import Loop, Compute, Uncompute, Control


if __name__ == "__main__":
    rotation_decomposition = RotationDecomposition()
    drawer = CircuitDrawer()
    eng = MainEngine(drawer, [rotation_decomposition])  # use default compiler engine
    
    x = eng.allocate_qubit()
    Rz(3.14/4) | x
    Measure | x

    print (drawer.get_latex())


