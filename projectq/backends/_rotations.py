#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Contains a compiler engine which counts the number of calls for each type of
gate used in a circuit, in addition to the max. number of active qubits.
"""
from projectq.cengines import LastEngineException, BasicEngine
from projectq.ops import FlushGate, Deallocate, Allocate, Measure, R, Rz, H, X, T, S
from projectq.ops import Command
import subprocess 

class RotationDecomposition(BasicEngine):
    """
    RotationDecomposition is a compiler engine which counts the number of gates and
    max. number of active qubits.

    Attributes:
        gate_counts (dict): Dictionary of gate counts.
            The keys are string representations of the gate.
        max_width (int): Maximal width (=max. number of active qubits at any
            given point).
    """
    def __init__(self):
        """
        Initialize a resource counter engine.

        Sets all statistics to zero.
        """
        BasicEngine.__init__(self)
        self._active_qubits = 0
        self._num_rotations = 0
        self._rotations = []


    def is_available(self, cmd):
        """
        Specialized implementation of is_available: Returns True if the
        ResourceCounter is the last engine (since it can count any command).

        Args:
            cmd (Command): Command for which to check availability (all
                Commands can be counted).

        Returns:
            availability (bool): True, unless the next engine cannot handle
                the Command (if there is a next engine).
        """
        try:
            return BasicEngine.is_available(self, cmd)
        except LastEngineException:
            return True

    def _is_rotation(self, cmd):
        if "Rz(" in str(cmd.gate) or "Ry(" in str(cmd.gate) or "Rx(" in str(cmd.gate):
            return True
        return False

    def _process_decomposition(self,decomp,qubit):
        new_sequence = []
        commands = list(decomp)
        for elem in reversed(commands):
            if elem == "H":
                new_sequence.append(Command(self,H,(qubit,)))
            elif elem == "T":
                new_sequence.append(Command(self,T,(qubit,)))
            elif elem == "S":
                new_sequence.append(Command(self,S,(qubit,)))
            elif elem == "X":
                new_sequence.append(Command(self,X,(qubit,)))
        return new_sequence

    def _decompose_rotation(self, cmd):
        """
        Decompose a single rotation instance
        """
    
        axis = None
        angle = 0
        gate_name = str(cmd.gate)

        if "Rz" in gate_name:
            axis = 'z'
        elif "Rx" in gate_name:
            axis = 'x'
        elif "Ry" in gate_name:
            axis = 'y' 

        angle = gate_name[gate_name.find("(")+1:gate_name.find(")")]

        decomposition = subprocess.check_output("./gridsynth " + angle, shell=True)[:-1]
        new_sequence = self._process_decomposition(str(decomposition),cmd.qubits[0])
        return new_sequence

    def _add_cmd(self, cmd):
        """
        Add a gate to the count.
        """
        if cmd.gate == Allocate:
            self._active_qubits += 1
        elif cmd.gate == Deallocate:
            self._active_qubits -= 1
        elif cmd.gate == Measure:
            for qureg in cmd.qubits:
                for qubit in qureg:
                    self.main_engine.set_measurement_result(qubit, 0)
        elif self._is_rotation(cmd):
            self._num_rotations += 1
            self._rotations.append(self._decompose_rotation(cmd))

    def __str__(self):
        """
        Return the string representation of this ResourceCounter.

        Returns:
            A string representation of the number of rotation gates encountered
        """
        return str(self._num_rotations) 

    def receive(self, command_list):
        """
        Receive a list of commands from the previous engine, print the
        commands, and then send them on to the next engine.

        Args:
            command_list (list<Command>): List of commands to receive (and
                count).
        """
        for cmd in command_list:
            if not cmd.gate == FlushGate():
                self._add_cmd(cmd)

            # (try to) send on
            if not self.is_last_engine:
                if self._is_rotation(cmd):
                    orig_cmd = cmd
                    sequence = self._rotations.pop(0)
                    for elem in sequence:
                        self.send([elem])
                else:
                    self.send([cmd])
