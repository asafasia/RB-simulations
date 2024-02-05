import numpy as np
import pygsti
from matplotlib import pyplot as plt
from pygsti.processors import QubitProcessorSpec as QPS
from pygsti.processors import CliffordCompilationRules as CCR
from qiskit import QuantumCircuit, execute, Aer, transpile
from qiskit_aer.noise import depolarizing_error, NoiseModel
from scipy.optimize import curve_fit
from rb_utils import decay_model, pygsti_to_qasm, qasm_to_qiskit

n_qubits = 4
qubit_labels = ['Q0', 'Q1', 'Q2', 'Q3']
gate_names = ['Gxpi2', 'Gxmpi2', 'Gypi2', 'Gympi2', 'Gcnot']
pspec = QPS(n_qubits, gate_names, qubit_labels=qubit_labels, geometry='ring')

compilations = {'absolute': CCR.create_standard(pspec, 'absolute', ('paulis', '1Qcliffords'), verbosity=0),
                'paulieq': CCR.create_standard(pspec, 'paulieq', ('1Qcliffords', 'allcnots'), verbosity=0)}

depths = range(0, 300, 10)
num_samples = 3
qubits = ['Q0', 'Q1', 'Q2', 'Q3']

sampler = 'edgegrab'
samplerargs = [0.9]
citerations = 20

randomizeout = True

design = pygsti.protocols.DirectRBDesign(pspec, compilations, depths, num_samples, qubit_labels=qubits, sampler=sampler,
                                         samplerargs=samplerargs, randomizeout=randomizeout,
                                         citerations=citerations)

circuits = design.all_circuits_needing_data
states = np.array(design.idealout_lists).flatten()

print(states)

qasm_circuits = pygsti_to_qasm(circuits)
qiskit_circuits = qasm_to_qiskit(qasm_circuits)

# print(qiskit_circuits[0])

# %%
# Error probabilities
prob_1 = 0.001  # 1-qubit gate
prob_2 = 0.01  # 2-qubit gate

error_1 = depolarizing_error(prob_1, 1)
error_2 = depolarizing_error(prob_2, 2)

noise_model = NoiseModel()
noise_model.add_all_qubit_quantum_error(error_1, ['x', 'rx', 'rz', 'u1', 'u2', 'u3'])
noise_model.add_all_qubit_quantum_error(error_2, ['cx'])

simulator = Aer.get_backend('aer_simulator')
circs = transpile(qiskit_circuits, simulator, basis_gates=["id", "sx", "x", "rz", "cx"])

# Run and get counts

print(qiskit_circuits[0])
result = simulator.run(circs,noise_model=noise_model,).result()


def get_probabilities(result):
    counts = result.get_counts()
    probabilities = []

    for i, count in enumerate(counts):
        state = states[i][::-1]
        probabilities.append(count.get(state) / 1024)

    new_probabilities = np.reshape(probabilities, (len(depths), num_samples))
    return new_probabilities


probabilities = get_probabilities(result)

mean_probabilities = np.mean(probabilities, axis=1)

# %%


args = curve_fit(decay_model, depths, mean_probabilities, p0=[0.5, 0.5, 0.9])
plt.plot(depths, mean_probabilities, '.', label='Simulated data')
plt.plot(depths, decay_model(depths, *args[0]), label='Fitted curve')
plt.title('direct RB')
plt.xlabel('Clifford Length')
plt.ylabel('Probability')
plt.ylim([0, 1])
plt.show()

r = 1 - args[0][2]
print(r)
