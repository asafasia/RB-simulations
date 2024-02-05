import numpy as np
from matplotlib import pyplot as plt
from qiskit import QuantumCircuit, execute

from qiskit_aer.noise import NoiseModel, depolarizing_error
from scipy.optimize import curve_fit

from main import circuits_rb_qiskit, circuits_per_depth, depths
from qiskit import Aer, transpile

# import qiskit.providers.aer.noise as noise
n = 1
d = 2 ** n

# Error probabilities
prob_1 = 0.03  # 1-qubit gate
prob_2 = 0.01  # 2-qubit gate

error_1 = depolarizing_error(prob_1, 1)
error_2 = depolarizing_error(prob_2, 1)

noise_model = NoiseModel()
noise_model.add_all_qubit_quantum_error(error_1, ['x', 'rx', 'rz'])
# noise_model.add_all_qubit_quantum_error(error_2, ['cx'])

simulator = Aer.get_backend('aer_simulator')
# circ = transpile(circuits_rb_qiskit, simulator)

# Run and get counts


result = execute(circuits_rb_qiskit, Aer.get_backend('qasm_simulator'),
                 noise_model=noise_model).result()


def get_result(result):
    counts = result.get_counts()
    probabilities = []
    for count in counts:
        probabilities.append(count['0'] / 1024)

    return np.reshape(probabilities, (len(depths), circuits_per_depth))


probabilities = get_result(result)

mean_probabilities = np.mean(probabilities, axis=1)

print(mean_probabilities)

depths = np.array(depths)


def decay_model(m, A, B, p):
    return A * p ** (m) + B


args = curve_fit(decay_model, depths, mean_probabilities, p0=[0.5, 0.5, 0.9])
rc = (d - 1) / d * (1 - args[0][2])
plt.plot(depths, mean_probabilities, '.', label='Simulated data')
plt.plot(depths, decay_model(depths, *args[0]), label='Fitted curve (p={:.3f})'.format(args[0][2]))

plt.xlabel('Depth')
plt.ylabel('Probability of measuring |0>')
plt.title('1q RB on Qiskit simulator')

plt.ylim([0, 1])
plt.legend()

plt.show()

print('fitting parameters: ', args[0])
print('clifford error rate: ', rc)
print('1-qubit error rate: ', rc / 5.7)
print('should be:',prob_1)


