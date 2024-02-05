import pygsti
from qiskit import QuantumCircuit
from qiskit_experiments.library import InterleavedRB, StandardRB
import numpy as np
import pygsti
from matplotlib import pyplot as plt
from pygsti.processors import QubitProcessorSpec as QPS
from pygsti.processors import CliffordCompilationRules as CCR
from qiskit import QuantumCircuit, execute, Aer, transpile
from qiskit_aer.noise import depolarizing_error, NoiseModel
from scipy.optimize import curve_fit
from rb_utils import pygsti_to_qasm, qasm_to_qiskit
from qiskit import qasm3


class RB_package:
    def __init__(self, type, qubits, depths, num_samples=1000, interleaved_element=None):
        self.qasm_circuits = None
        self.qiskit_circuits = None
        self.pygsti_circuits = None
        self.type = type
        self.qubits = qubits
        self.num_samples = num_samples
        self.depths = depths
        self.interleaved_element = interleaved_element
        self.generate_circuits()
        self._is_qiskit_setter()
        self.tranpsile_circuits()
        self.translate_circuits_to_qasm()
        if self.is_qiskit:
            self.circuits = self.qiskit_circuits
        else:
            self.circuits = self.pygsti_circuits
    def _is_qiskit_setter(self):
        if self.type == 'standard' or self.type == 'interleaved':
            self.is_qiskit = True
        else:
            self.is_qiskit = False

    def generate_circuits(self):
        if self.type == 'standard':
            self._generate_standard_circuits()
        elif self.type == 'interleaved':
            self._generate_interleaved_circuits()
        elif self.type == 'direct':
            self._generate_direct_circuits()

    def _generate_standard_circuits(self):
        circuits = StandardRB(
            physical_qubits=self.qubits,
            num_samples=self.num_samples,
            lengths=self.depths,
        ).circuits()

        self.qiskit_circuits = circuits

    def _generate_pure_circuits(self):
        # todo add tomography
        circuits = StandardRB(
            physical_qubits=self.qubits,
            num_samples=self.num_samples,
            lengths=self.depths,
            interleaved_element=self.interleaved_element,
            circuit_order='RRRIII'
        ).circuits()

    def _generate_interleaved_circuits(self):
        if self.interleaved_element is None:
            raise ValueError("Interleaved element is None")

        circuits = InterleavedRB(
            physical_qubits=self.qubits,
            num_samples=self.num_samples,
            lengths=self.depths,
            interleaved_element=self.interleaved_element,
            circuit_order='RRRIII'
        ).circuits()

        self.qiskit_circuits = circuits

    def _generate_direct_circuits(self):
        n_qubits = len(self.qubits)

        qubit_labels = [f'Q{i}' for i in self.qubits]

        gate_names = ['Gxpi2', 'Gxmpi2', 'Gypi2', 'Gympi2', 'Gcnot']

        pspec = QPS(n_qubits, gate_names, qubit_labels=qubit_labels, geometry='ring')

        compilations = {'absolute': CCR.create_standard(pspec, 'absolute', ('paulis', '1Qcliffords'), verbosity=0),
                        'paulieq': CCR.create_standard(pspec, 'paulieq', ('1Qcliffords', 'allcnots'), verbosity=0)}

        sampler = 'edgegrab'
        samplerargs = [0.25]
        citerations = 20
        randomizeout = True

        design = pygsti.protocols.DirectRBDesign(pspec, compilations,
                                                 self.depths,
                                                 self.num_samples,
                                                 qubit_labels=qubit_labels,
                                                 sampler=sampler,
                                                 samplerargs=samplerargs,
                                                 randomizeout=randomizeout,
                                                 citerations=citerations)

        self.pygsti_circuits = design.all_circuits_needing_data

    def translate_circuits_to_qasm(self):
        qasm_circs = []
        if self.is_qiskit:
            for circ in self.qiskit_circuits:
                qasm = qasm3.dumps(circ)
                qasm_circs.append(qasm)

        else:
            for circ in self.pygsti_circuits:
                qasm_circs.append(circ.convert_to_openqasm(standard_gates_version="u3"))

        self.qasm_circuits = qasm_circs

    def tranpsile_circuits(self):
        if self.is_qiskit:
            self.qiskit_circuits = transpile(self.qiskit_circuits, basis_gates=["id", "sx", "x", "rz", "cx"])

    def qasm_circuits(self):
        return self.qasm_circuits


args = {
    'type': 'standard',
    'qubits': [0],
    'depths': [1, 10, 20, 30, 40, 50],
    'num_samples': 2,
    'interleaved_element': None

}

# circuit_generator = RB_package(**args)

# # print(circuit_generator.pygsti_circuits)
# print(circuit_generator.qiskit_circuits[0])
# print(circuit_generator.qasm_circuits[2])
