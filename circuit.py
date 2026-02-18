from bloqade import qasm2
from bloqade.pyqrack import StackMemorySimulator
from gates import h_parallel


class Circuit:
    def __init__(self, kernel, num_qubits):
        self.kernel = kernel
        self.num_qubits = num_qubits

    @staticmethod
    def _get_probs(result):
        return {
            "".join(str(bit.value) for bit in bitstr): prob
            for bitstr, prob in result.items()
        }

    def measure_z_basis(self, num_shots):
        @qasm2.extended
        def kernel():
            qreg = qasm2.qreg(self.num_qubits)
            creg = qasm2.creg(self.num_qubits)
            self.kernel(qreg, creg)
            qasm2.measure(qreg, creg)
            return creg

        sim = StackMemorySimulator(min_qubits=self.num_qubits)
        res = sim.task(kernel=kernel).batch_run(shots=num_shots)
        probs = self._get_probs(result=res)
        return probs

    def measure_x_basis(self, num_shots):
        @qasm2.extended
        def kernel():
            qreg = qasm2.qreg(self.num_qubits)
            creg = qasm2.creg(self.num_qubits)
            self.kernel(qreg, creg)
            h_parallel(qreg)
            qasm2.measure(qreg, creg)
            return creg

        sim = StackMemorySimulator(min_qubits=self.num_qubits)
        res = sim.task(kernel=kernel).batch_run(shots=num_shots)
        probs = self._get_probs(result=res)
        return probs
