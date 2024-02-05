import numpy as np
from matplotlib import pyplot as plt
from qiskit import QuantumCircuit, execute

from qiskit import qasm3, transpile, QuantumCircuit, Aer
from qiskit_aer.noise import depolarizing_error, NoiseModel
from qiskit_experiments.library import InterleavedRB
from scipy.optimize import curve_fit

interleaved_element = QuantumCircuit(1)
interleaved_element.x(0)

depths = np.array(range(1, 200, 1))

num_samples = 10

qubits = [0]

ground_state = '0' * len(qubits)

qiskit_experiment = InterleavedRB(
    physical_qubits=[0],
    num_samples=num_samples,
    lengths=depths,
    interleaved_element=interleaved_element,
    circuit_order='RRRIII'
).circuits()

transpiled_circuit = transpile(
    qiskit_experiment, basis_gates=["id", "sx", "x", "rz", "cx"]
)

# Error probabilities
prob_1 = 0.02  # 1-qubit gate
prob_2 = 0.01  # 2-qubit gate

error_1 = depolarizing_error(prob_1, 1)
error_2 = depolarizing_error(prob_2, 1)

noise_model = NoiseModel()
noise_model.add_all_qubit_quantum_error(error_1, ['x', 'rx', 'rz'])
# noise_model.add_all_qubit_quantum_error(error_2, ['cx'])

simulator = Aer.get_backend('aer_simulator')
# circ = transpile(circuits_rb_qiskit, simulator)

# Run and get counts


result = execute(transpiled_circuit, Aer.get_backend('qasm_simulator'),
                 noise_model=noise_model).result()


def get_result(result):
    counts = result.get_counts()[0:len(depths) * num_samples]
    interleaved_counts = result.get_counts()[len(depths) * num_samples:]

    probabilities = []
    interleaved_probabilities = []

    for count in counts:
        probabilities.append(count[ground_state] / 1024)

    for count in interleaved_counts:
        interleaved_probabilities.append(count[ground_state] / 1024)

    new_probabilities = np.reshape(probabilities, (num_samples, len(depths)))
    new_interleaved_probabilities = np.reshape(interleaved_probabilities, (num_samples, len(depths)))

    return new_probabilities, new_interleaved_probabilities


probabilities, interleaved_probabilities = get_result(result)

mean_probabilities = np.mean(probabilities, axis=0)
mean_interleaved_probabilities = np.mean(interleaved_probabilities, axis=0)


def decay_model(m, A, B, p):
    return A * p ** m + B


args = curve_fit(decay_model, depths, mean_probabilities, p0=[0.5, 0.5, 0.9])
args_interleaved = curve_fit(decay_model, depths, mean_interleaved_probabilities, p0=[0.5, 0.5, 0.9])

plt.plot(depths, mean_probabilities, '.', label='Simulated data')
plt.plot(depths, mean_interleaved_probabilities, '.', label=f'Simulated data interleaved')

plt.plot(depths, decay_model(depths, *args[0]), label=f'Fitted curve p = {args[0][2]:.3f}')
plt.plot(depths, decay_model(depths, *args_interleaved[0]),
         label=f'Fitted curve interleaved p = {args_interleaved[0][2]:.3f}')

plt.legend()
plt.title('Interleaved RB')
plt.xlabel('Depth')
plt.ylabel('Probability of measuring |0>')
d = 2
rc = (d - 1) / d * (1 - args[0][2])
rc_interleaved = (d - 1) / d * (1 - args_interleaved[0][2] / args[0][2])

print('rc', rc)
print('rc interleaved', rc_interleaved)
print('should be ', prob_1 / 2)
plt.show()
