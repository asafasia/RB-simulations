from qiskit import QuantumCircuit


def decay_model(m, A, B, p):
    return A * p ** m + B


def pygsti_to_qasm(circuits):
    circuits_Qasm = []
    for circuit in circuits:
        circuits_Qasm.append(circuit.convert_to_openqasm(standard_gates_version="u3"))  # x-sx-rz or u3

    return circuits_Qasm


def qasm_to_qiskit(circuits):
    circuits_qiskit = []
    for circuit in circuits:
        circuits_qiskit.append(QuantumCircuit.from_qasm_str(circuit))

    return circuits_qiskit


