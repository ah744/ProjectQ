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
Tests for projectq.backends._resource.py.
"""

import pytest

from projectq.cengines import MainEngine, DummyEngine
from projectq.ops import H, CNOT, X, Measure, R, Rz

from projectq.backends import RotationDecomposition 


class MockEngine(object):
    def is_available(self, cmd):
        return False


def test_rotation_decomposition_isavailable():
    rotation_decomposition = RotationDecomposition()
    rotation_decomposition.next_engine = MockEngine()
    assert not rotation_decomposition.is_available("test")
    rotation_decomposition.next_engine = None
    rotation_decomposition.is_last_engine = True

    assert rotation_decomposition.is_available("test")


def test_rotation_decomposition():
    rotation_decomposition = RotationDecomposition()
    backend = DummyEngine(save_commands=True)
    next_engine = DummyEngine(save_commands=True)
    rotation_decomposition.next_engine = next_engine
    eng = MainEngine(backend, [rotation_decomposition])

    qubit1 = eng.allocate_qubit()
    qubit2 = eng.allocate_qubit()
    Rz(3.14/4) | qubit1
    Measure | (qubit1)
    assert int(qubit1) == 0
    assert str(rotation_decomposition) == "1" 

    sent_gates = [cmd.gate for cmd in next_engine.received_commands]
    assert sent_gates.count(Measure) == 1


def test_rotation_decomposition_str_when_empty():
    assert isinstance(str(RotationDecomposition()), str)
