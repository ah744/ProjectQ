import math
import numpy as np

from projectq import MainEngine
import projectq.setups.ibm
from projectq.backends import CircuitDrawer
from projectq.backends import CommandPrinter 
from projectq.backends import IBMBackend 
from projectq.cengines import IBMCNOTMapper
from projectq.backends import RotationDecomposition 
from projectq.ops import H, Z, X, Measure, All, R, CNOT, Rz, T, S
from projectq.meta import Loop, Compute, Uncompute, Control

def CZ(q1, q2, phi):
    Rz( -2*phi ) | q2
    CNOT | (q1, q2)
    Rz( phi ) | q2
    CNOT | (q1, q2)

def ZcrossZ(q1, q2, phi):
    Rz(phi) | q1
    Rz(-1*phi) | q2
    CZ(q1,q2,-2*phi)

def Red(qubits, m, J, M):
    for n in range(0,len(qubits)-1,2):
        phi = J[n] * (2.0*m - 1)/M
        ZcrossZ(qubits[n], qubits[n+1], phi)

def Black(qubits, m, J, M):
    for n in range(1,len(qubits)-1,2):
        phi = J[n] * (2.0*m - 1)/M
        ZcrossZ(qubits[n], qubits[n+1], phi)

def Inter(qubits, m, Bx, Bz, T, M):
    theta1 = (1.0 - (2.0*m - 1)/M) * -2 * Bx * T / M
    for n in range(len(qubits)):
        theta2 = (1.0 - (2.0*m-1)/M)* -2 * Bz[n] * T / M
        H | qubits[n]
        Rz(theta1) | qubits[n]
        H | qubits[n]
        Rz(theta2) | qubits[n]

def run_ising(eng, N, Bx, Bz, J, M, T):
    """
    Runs Ising Model Hamiltonian simulation on n = N qubits 
    Args:
        eng (MainEngine): Main compiler engine to run Ising on.
        N (int): Number of bits in the problem.
        Bx (int): Bound on range of randomized rotations
        M:  Number of Trotter steps to perform
        T:  Total duration of adiabatic evolution
    Returns:
        solution (list<int>): Solution bit-string.
    """
    x = eng.allocate_qureg(N)

    # start in uniform superposition
    All(H) | x
    for m in range(M):
        Red(x, m, J, M)
        Black(x, m, J, M)
        Inter(x, m, Bx, Bz, T, M)

    Measure | x 
    eng.flush()

      # return result
    return [int(qubit) for qubit in x]

if __name__ == "__main__":
    drawing_engine = CircuitDrawer()
    command_printer = CommandPrinter()
    rotation_decomposition = RotationDecomposition()
    ibm = IBMBackend(use_hardware=True, num_runs=1024,verbose=True)
    eng = MainEngine(drawing_engine, [rotation_decomposition])  # use rotation decomposition first

    Bx = 2
    M = 25 
    T = 15
    N = 5 
    Bz = np.random.uniform(-Bx,Bx,N)
    J = np.random.uniform(-Bx,Bx,N)

    # run Ising Model with n = N qubits 
    print(run_ising(eng, N, Bx, Bz, J, M, T))
    print(drawing_engine.get_latex())
