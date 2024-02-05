from pprint import pprint

import numpy as np
import pygsti
from pygsti.processors import QubitProcessorSpec as QPS
from pygsti.processors import CliffordCompilationRules as CCR
from qiskit import qasm3, transpile
from qiskit import Aer, transpile

# Define pyGSTi 2 Qubit RB circuit

n_qubits = 1
qubit_labels = ["Q0"]
gate_names = ['Gxpi2', 'Gxmpi2', 'Gypi2', 'Gympi2', 'Gcphase']
# Uncomment below for more qubits or to use a different set of basis gates
# n_qubits = 4
# qubit_labels = ['Q0','Q1','Q2','Q3']
# gate_names = ['Gxpi2', 'Gxmpi2', 'Gypi2', 'Gympi2', 'Gcnot']
# availability = {'Gcphase':[('Q0','Q1'), ('Q1','Q2'), ('Q2','Q3'), ('Q3','Q0')]}

pspec = QPS(n_qubits, gate_names, availability=None, qubit_labels=qubit_labels)

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

c = Circuit([('Gxpi2')], line_labels=['Q0'])
print(c)
design = pygsti.protocols.CliffordRBDesign(
    pspec,
    compilations,
    depths,
    circuits_per_depth,
    qubit_labels=qubits,
    randomizeout=randomizeout,
    citerations=citerations,
    interleaved_circuit=c

)

circuits_rb = design.all_circuits_needing_data
print(circuits_rb[0])
