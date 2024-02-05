from pprint import pprint

import numpy as np
import pygsti
from pygsti.processors import QubitProcessorSpec as QPS
from pygsti.processors import CliffordCompilationRules as CCR
from qiskit import qasm3, transpile
from qiskit import Aer, transpile

# Define pyGSTi 2 Qubit RB circuit

n_qubits = 2
qubit_labels = ["Q0", "Q1"]
gate_names = ["Gxpi", "Gxpi2", "Gypi", "Gypi2", "Gcphase"]
availability = {"Gcphase": [("Q0", "Q1")]}

# Uncomment below for more qubits or to use a different set of basis gates
# n_qubits = 4
# qubit_labels = ['Q0','Q1','Q2','Q3']
# gate_names = ['Gxpi2', 'Gxmpi2', 'Gypi2', 'Gympi2', 'Gcnot']
# availability = {'Gcphase':[('Q0','Q1'), ('Q1','Q2'), ('Q2','Q3'), ('Q3','Q0')]}

pspec = QPS(n_qubits, gate_names, availability=availability, qubit_labels=qubit_labels)

compilations = {
    "absolute": CCR.create_standard(
        pspec, "absolute", ("paulis", "1Qcliffords"), verbosity=0
    ),
    "paulieq": CCR.create_standard(
        pspec, "paulieq", ("1Qcliffords", "allcnots"), verbosity=0
    ),
}

depths = range(0, 100, 10)
circuits_per_depth = 10

qubits = ["Q0"]

randomizeout = False
citerations = 1
from pygsti.circuits import Circuit

c = Circuit([('Gxpi', 0)])
print()
design = pygsti.protocols.CliffordRBDesign(
    pspec,
    compilations,
    depths,
    circuits_per_depth,
    qubit_labels=qubits,
    randomizeout=randomizeout,
    citerations=citerations,
    interleaved_circuit=None

)

circuits_rb = design.all_circuits_needing_data
print(circuits_rb[0])

# %%


def convert_to_Qasm(circuits):
    circuits_Qasm = []
    for circuit in circuits:
        circuits_Qasm.append(circuit.convert_to_openqasm(standard_gates_version="x-sx-rz"))

    return circuits_Qasm


circuits_rb_Qasm = convert_to_Qasm(circuits_rb)

circuits_rb_qiskit = []
from qiskit import QuantumCircuit

new_vector = []

for value in depths:
    new_vector.extend([value] * circuits_per_depth)

print(new_vector)

mean_len = []

for i, circuit in enumerate(circuits_rb_Qasm):
    qiskit_circ = transpile(QuantumCircuit.from_qasm_str(circuit),basis_gates=['x', 'sx', 'rz'], optimization_level=3)

    gates_lengths = dict(qiskit_circ.count_ops())
    rz = gates_lengths.get('rz')
    x = gates_lengths.get('x')
    sx = gates_lengths.get('sx')

    if rz is None:
        rz = 0
    if x is None:
        x = 0
    if sx is None:
        sx = 0

    s = rz + x + sx
    print(gates_lengths)

    print(s)
    print((new_vector[i] + 1))
    # length = s[i]/new_vector[i]

    mean_len.append(s / (new_vector[i] + 1))

    # print(gates_lengths['sx'], gates_lengths['x'], gates_lengths['rz'])
    # number_of_gates = gates_lengths['sx'] + gates_lengths['rz'] + gates_lengths['x']
    # print(number_of_gates)

    circuits_rb_qiskit.append(qiskit_circ)

print(circuits_rb_qiskit[-1])
print(np.mean(mean_len))
